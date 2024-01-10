import json
from zipfile import BadZipFile

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import PasswordChangeView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Value, IntegerField, JSONField
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from .forms import *
from .models import *
from .choices import DIVISA_CHOICES, TASA_CHOICES
from .scriptModels import *
from .decorators import *
from datetime import date, datetime
from django.utils import formats
from BAapp.utils.utils import *
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.datastructures import MultiValueDictKeyError
from .utils.email_send import email_send
from django.contrib.sites.models import Site
import ast
from django.conf import settings
from decimal import *
from BAapp.utils.formatusd import to_input_string
from django.template.loader import get_template
from BAapp.utils.negocios_helper import listasNA, listaNL, semaforoVencimiento, calcularVencAtr
import weasyprint
import os
import PyPDF2
import shutil

User = settings.AUTH_USER_MODEL

def cuentas(request):
    return render(request, 'cuentas.html')

def admin(request):
    return render(request,'admin.html')

def chat(request):
    return render(request,'chat.html')


# los nuevos views

class Inicio(View):
    def get(self, request, *args, **kwargs):
        return render(request,'inicio.html')

class NuevoNegocioView(View):
    def get(self, request, *args, **kwargs):
        return render(request,'nuevo_negocio.html')

class TodoseNegociosView(View):
    def get(self, request, *args, **kwargs):
        vendedores = todos_negocios_vendedor_query(request.user)
        return render(request, 'todos_los_negocios.html', {'todos_vendedores':vendedores})
    
def todos_negocios_vendedor_query(user):
    negocios = Negocio.objects.filter(comprador=user)
    lista_vendedores = []
    for negocio in negocios:
        vendedor_pk = negocio.vendedor.pk
        if vendedor_pk not in set(lista_vendedores):
            lista_vendedores.append(vendedor_pk)
    vendedores = MyUser.objects.filter(pk__in=lista_vendedores)
    return vendedores

class Info_negocioView(View): 
    def get(self, request, *args, **kwargs):
        if ("pk" in kwargs):
            idNeg = kwargs["pk"]
            negocio = Negocio.objects.get(id_de_neg=idNeg)
            propuesta = Propuesta.objects.filter(negocio=negocio).order_by('-pk').first()
            idProp = propuesta.id
            grupo_activo = request.user.clase
            envio = propuesta.envio_comprador
            if (grupo_activo == 'Comprador' or grupo_activo == 'Gerente'):
                envio = not envio
            items = None
            persona = request.user
            if (grupo_activo == 'Logistica'):
                items = ItemPropuesta.objects.filter(propuesta__id = idProp, empresa__id=persona.empresa.id)
            elif (grupo_activo == 'Administrador'):
                items = ItemPropuesta.objects.filter(propuesta__id = idProp, empresa__id=persona.empresa.id)
            elif (grupo_activo == 'Proveedor'):
                items = ItemPropuesta.objects.filter(propuesta__id = idProp, proveedor__id=persona.id) 
            else:
                items = ItemPropuesta.objects.filter(propuesta__id = idProp) 
                facturas = Factura.objects.filter(negocio=propuesta.negocio)
                remitos = Remito.objects.filter(negocio=propuesta.negocio)
                ordenesDeCompra = OrdenDeCompra.objects.filter(negocio=negocio)
                ordenesDePago = OrdenDePago.objects.filter(negocio=negocio)
                constancias = ConstanciaRentencion.objects.filter(negocio=negocio)
                recibos = Recibo.objects.filter(negocio=negocio)
                cheques = Cheque.objects.filter(negocio=negocio)
                cuentasCorriente = CuentaCorriente.objects.filter(negocio=negocio)
                facturasComision = FacturaComision.objects.filter(negocio=negocio)
                notas = Nota.objects.filter(negocio=negocio)
                comprobantes = {
                    "facturas": facturas,
                    "remitos": remitos,
                    "ordenesDeCompra": ordenesDeCompra,
                    "ordenesDePago": ordenesDePago,
                    "constancias": constancias,
                    "recibos": recibos,
                    "cheques": cheques,
                    "cuentasCorriente": cuentasCorriente,
                    "facturasComision": facturasComision,
                    "notas": notas,          
                }   
            return render (request, 'info_negocio.html', {'negocio':negocio, 'items':list(items), "comprobantes":comprobantes,})

def comprobanteTipo(num):
    options = {
            '1': "FACTURA",
            '2': "REMITO",
            '3': "ORDEN DE COMPRA",
            '4': "ORDEN DE PAGO",
            '5': "CONSTANCIA DE RETENCION",
            '6': "RECIBO",
            '7': "CHEQUE",
            '8': "CUENTA CORRIENTE",
            '9': "FACTURA COMISION",
            '10': "NOTA",
            'default': "casi",
        }
    return options.get(num)

class ComprobantesView(View):
    def get(self, request, *args, **kwargs):
        moment_url = request.resolver_match.url_name
        if moment_url=="facturas":
            num = 1
            data = Factura.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(proveedor=request.user))
            campos = Factura._meta.get_fields()
        elif moment_url=="remitos":
            num = 2
            data = Remito.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(proveedor=request.user))
            campos = Remito._meta.get_fields()
        elif moment_url=="ordenesCompras":
            num = 3
            data = OrdenDeCompra.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
            campos = OrdenDeCompra._meta.get_fields()
        elif moment_url=="ordenesPagos":
            num = 4
            data = OrdenDePago.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
            campos = OrdenDePago._meta.get_fields()
        elif moment_url=="contancias":
            num = 5
            data = ConstanciaRentencion.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
            campos = ConstanciaRentencion._meta.get_fields()
        elif moment_url=="recibos":
            num = 6
            data = Recibo.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
            campos = Recibo._meta.get_fields()
        elif moment_url=="cheques":
            num = 7
            data = Cheque.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))
            campos = Cheque._meta.get_fields()
        elif moment_url=="cuentasCorrientes":
            num = 8
            data = CuentaCorriente.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))
            campos = CuentaCorriente._meta.get_fields()
        elif moment_url=="facturasComision":
            num = 9
            data = FacturaComision.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
            campos = FacturaComision._meta.get_fields()
        elif moment_url=="notas":
            num = 10
            data = Nota.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))
            campos = Nota._meta.get_fields()
        else:
            data = {}
            campos = []
            print("error: comprobante no valido")

        camposNombres = []
        metaNombres = []
        for campo in campos:
            # splits
            barsplit = campo.name.split("_")
            dotsplit = str(campo).split(".")

            # nombres de titulos
            try:
                nombre = barsplit[1]
            except:
                nombre = barsplit[0]
            
            if(nombre == "numero"):
                nombre = barsplit[0]
            camposNombres.append(nombre)

            # metaNombres
            try:    
                metaNombres.append(dotsplit[2])
            except: 
                metaNombres.append(str(campo))
            

        largo = len(camposNombres)-1
        camposNombres = camposNombres[2:largo]
        metaNombres = metaNombres[2:largo]

        tipo = comprobanteTipo(str(num))

        return render(request, 'comprobantes.html',{"num": num,"tipo": tipo, "data":data, "camposNombres":camposNombres, "campos":metaNombres})

class MenuComprobantesView(View):
    def get(self, request, *args, **kwargs):
        lista_comprobantes = [{"nombre":"Facturas",
                            "url": "facturas"},
                        {"nombre":"Remitos",
                            "url": "remitos"},
                        {"nombre":"Orden de compra",
                            "url": "ordenesCompras"},
                        {"nombre":"Orden de pago",
                            "url": "ordenesPagos"},
                        {"nombre":"Constancia rentención",
                            "url": "contancias"},
                        {"nombre":"Recibo",
                            "url": "recibos"},
                        {"nombre":"Cheques",
                            "url": "cheques"},
                        {"nombre":"Cuentas corrientes",
                            "url": "cuentasCorrientes"},
                        {"nombre":"Factura comisiones",
                            "url": "facturasComision"},
                        {"nombre":"Nota",
                            "url": "notas"}, 
                        ]
        return render(request, 'menu_comprobantes.html',{"lista_comprobantes":lista_comprobantes})


class NotificacionesView(View):
    def get(self, request, *args, **kwargs):
        #lpn = Lista Presupuesto Notificaciones
        lpn = Notificacion.objects.filter(user=request.user, categoria__contains='Presupuesto').order_by('-timestamp')
        #lln = Lista Logistica Notificaciones
        lln = Notificacion.objects.filter(user=request.user, categoria__contains='Logistica').order_by('-timestamp')
        #lvn = Lista Vencimiento Notificaciones
        lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
        context = {
            'lista_vencimiento': lvn,
            'lista_logistica_noti': lln,
            'lista_presupuestos': lpn
        }
        return render(request, 'notificaciones.html', context)

class PresupuestosView(View):
    def get(self, request, *args, **kwargs):
        #Negocios en Procesos    
        negociosAbiertos = get_negocios_bygroup(request, True)
        lnr = listasNA(negociosAbiertos, True)
        lnp = listasNA(negociosAbiertos, False)
        vendedores = MyUser.objects.filter(clase='Vendedor')
        context = {
            'presupuestos_recibidos': list(lnr),
            'presupuestos_negociando': list(lnp),
            'todos_vendedores': vendedores
        }
        return render(request, 'presupuestos.html', context)

def get_negocios_bygroup(request, fcn):
    clase_usuario = request.user.clase
    #A = Administrador 
    if (clase_usuario == "Administrador"):
        negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=fcn, comprador__empresa=request.user.empresa).values_list('id', flat=True).order_by('-timestamp').distinct())
    #C = Comprador
    elif (clase_usuario == "Comprador"):
        negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=fcn, comprador__id=request.user.id).values_list('id', flat=True).order_by('-timestamp').distinct())
    #V = Vendedor
    elif (clase_usuario == "Vendedor"):
        negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=fcn).values_list('id', flat=True).order_by('-timestamp').distinct())
    else:
        negociosAbiertos = []
    return negociosAbiertos

class VencimientosView(View):
    def get(self, request, *args, **kwargs):
        #negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())                    
        negociosCerrConf = get_negocios_bygroup(request, False)
        lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
        lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
        return render(request, 'vencimientos.html', {'lista_vencimiento':lvn,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos})

class LogisticaView(View):
    def get(self, request, *args, **kwargs):
        negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, estado="CONFIRMADO").values_list('id', flat=True).order_by('-timestamp').distinct())    
        lnl = listaNL(request, negociosCerrConf)
        return render(request, 'logistica.html',{'lista_logistica':lnl})

def detalleNotis(request):
    if request.method == 'POST':
        idNoti = request.POST['idNoti']        
        notificacion = Notificacion.objects.get(id=int(idNoti))        
        first = notificacion.hyperlink.split("/",1)[1]
        idNegocio = first.split("/",1)[1]
        negocio = Negocio.objects.get(id=int(idNegocio))
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','envio_comprador')[:1])
        if (not propuesta):
            return render (request, 'modalnotis.html')
        else:
            id_prop = propuesta[0][0]
            negocio.id_prop = id_prop
            return render (request, 'modalnotis.html', {'notificacion':notificacion,'negocio':negocio})
    return render (request, 'modalnotis.html')


#lo viejo xd

def getNegociosByClase(request, user_clase, tipo):
    negocio = []
    # vendedor
    if (user_clase == 'Vendedor'):
        if (tipo == 2):
            negocio = Negocio.objects.all().values_list('id', flat=True)
        else:
            negocios = Negocio.objects.all().order_by('-last_modified', '-timestamp')
            negocio = getNegociosToList(negocios)
            for a in negocio:
                a.proveedores = getProveedoresNegocio(a)

    # Comprador
    elif (user_clase == 'Comprador'):
        if (tipo == 2):
            negocio = Negocio.objects.filter(comprador=request.user).order_by('-last_modified', '-timestamp').values_list('id', flat=True)
        else:
            negocios = Negocio.objects.filter(comprador=request.user).order_by('-last_modified', '-timestamp')
            negocio = getNegociosToList(negocios)
    
    # Gerente
    elif (user_clase == 'Gerente'):
        mi_gerente = request.user
        if (tipo == 2):
            negocio = Negocio.objects.filter(comprador__empresa__id=mi_gerente.empresa.id).order_by('-last_modified', '-timestamp').values_list('id', flat=True)
        else:
            negocios = Negocio.objects.filter(comprador__empresa__id=mi_gerente.empresa.id).order_by('-last_modified', '-timestamp')
            negocio = getNegociosToList(negocios)

    # proveedor
    elif (user_clase == 'Proveedor'):
        negocios = Negocio.objects.filter(fecha_cierre__isnull=False).order_by('-last_modified', '-timestamp')
        lista_ids = []
        for a in negocios:
            empleadoP = request.user
            id_prop = Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id', flat=True)[:1]
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop, proveedor__id=empleadoP.id)
            if (len(items) > 0):                
                lista_ids.append(a.id)
        if (tipo == 2):
            negocio = lista_ids
        else:
            negocios = Negocio.objects.filter(id__in=lista_ids).order_by('-last_modified', '-timestamp')
            negocio = getNegociosToList(negocios)

    # administrador
    elif (user_clase == 'Administrador'):
        negocios = Negocio.objects.filter(comprador__empresa=request.user.empresa).order_by('-last_modified', '-timestamp')
        lista_ids = []
        for a in negocios:
            empleadoA = request.user
            id_prop = Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id', flat=True)[:1]
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=empleadoA.empresa.id)
            if (len(items) > 0):
                lista_ids.append(a.id)
        if (tipo == 2):
            negocio = lista_ids
        else:
            negocios = Negocio.objects.filter(id__in=lista_ids).order_by('-timestamp')
            negocio = getNegociosToList(negocios)
    else:
        negocio = []
    return negocio


def todosFiltro(request, tipo):
    negocios_permitidos = getNegociosByClase(request,request.user.clase,2)
    negocio = []
    negocioAux = []
    estado = ""
    if (int(tipo) == 1):
        estado = "Recibido"
    elif (int(tipo) == 2):
        estado = "En Negociación"
    elif (int(tipo) == 3):
        estado = "Confirmado"
    else:
        estado = "Cancelado"
    todos_negocios = Negocio.objects.filter(id__in=negocios_permitidos)
    for a in todos_negocios:
        propuesta = Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp')[:1]
        propuesta = list(Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id','envio_comprador')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            envio = propuesta[0][1]
            if (request.user.clase == 'Comprador' or request.user.clase == 'Gerente'):
                envio = not envio
            a.id_prop = id_prop
    for b in todos_negocios:        
        if (b.estado == estado):
            b.proveedores = getProveedoresNegocio(b)
            negocioAux.append(b)
    vendedores = MyUser.objects.filter(clase='Vendedor')   
    return render(request, 'todos_los_negocios.html', {'todos_negocios':list(negocioAux), 'todos_vendedores':vendedores})

def filtrarNegocios(request):
    vendedores = request.POST['vendedor']
    estados = request.POST['estado']
    tipo = request.POST['tipo']
    fecha_desde = request.POST['fechaDesde']
    fecha_hasta = request.POST['fechaHasta']
    idDeNeg = request.POST['idDeNeg']

    if request.user.is_staff:
        filters = Q()
    else:
        filters = Q(vendedor=request.user) | Q(comprador=request.user)

    if vendedores != 'todos':
        list_vendedores_str = ast.literal_eval(vendedores)
        list_vendedores = [int(item) for item in list_vendedores_str]
        filters &= Q(vendedor__pk__in=list_vendedores)
    if estados != 'todos':
        list_estados = ast.literal_eval(estados)
        if "CONFIRMADO" in list_estados:
            list_estados.append("YA_CONFIRMADO")
        filters &= Q(estado__in=list_estados)
    if tipo != 'todos':
        filters &= Q(tipo_de_negocio=tipo)
    if fecha_desde:
        fecha_format = parse_date(fecha_desde)
        filters &= Q(timestamp__gte=fecha_format)
    if fecha_hasta:
        fecha_format = parse_date(fecha_hasta)
        filters &= Q(timestamp__lte=fecha_format)
    if idDeNeg:
        id_de_neg = int(idDeNeg)
        filters &= Q(id_de_neg=id_de_neg)

    todos_los_negocios = Negocio.objects.filter(filters).annotate(
        id_prop=Value(1, output_field=IntegerField()),
        proveedores=Value([], output_field=JSONField())
        ).order_by('-last_modified', '-timestamp')

    for neg in todos_los_negocios:
        try:
            prop = Propuesta.objects.filter(negocio=neg).last()
            neg.id_prop = prop.id

            if neg.is_confirmado():
                item_prop_list = ItemPropuesta.objects.filter(propuesta=prop)
                neg.proveedores = populate_proveedores(item_prop_list)
        except AttributeError:
            print(f"El negocio {neg.get_id_de_neg()} no posee propuestas")

    return render(request, 'tempAux/tableNegociosFiltros.html', {'todos_negocios':todos_los_negocios})

def parse_date(date):
    formatted_date = timezone.datetime.strptime(date, '%d/%m/%Y').date()
    aware_date = timezone.make_aware(timezone.datetime.combine(formatted_date, timezone.datetime.min.time()))
    return aware_date

def populate_proveedores(item_prop_query):
    proveedores = []
    for item in item_prop_query:
        prov_name = item.proveedor.get_full_name()
        if prov_name not in set(proveedores):
            proveedores.append(prov_name)

    return proveedores

def getProveedoresNegocio(negocio):
    proveedores = []
    if (negocio.fecha_cierre is not None):
        items = ItemPropuesta.objects.filter(propuesta__negocio__id = negocio.id)
        proveedores = []
        id_proveedores = [] 
        for b in items:
            if (b.proveedor and b.proveedor.id not in id_proveedores):
                id_proveedores.append(b.proveedor.id)
                prov = b.proveedor.get_full_name()
                proveedores.append(prov)
    return proveedores

def merge_pdfs(input_pdfs, output_pdf):
    pdf_merger = PyPDF2.PdfMerger()

    for pdf in input_pdfs:
        pdf_merger.append(pdf)

    pdf_merger.write(output_pdf)
    pdf_merger.close()

def generar_pdf(context, request):
    titulo = context.get('titulo')
    texto = context.get('texto')
    observaciones = context.get('obs')
    propuesta = context.get('prop')
    items_prop = context.get('articulos')
    negocio = context.get('negocio')
    
    context_hoja1 = {'titulo': titulo, 'texto': texto, 'obs': observaciones, 'prop': propuesta, 'negocio': negocio}
    hoja1_template = get_template('email/pdf_resumen_hoja1.html')
    hoja1_html = hoja1_template.render(context_hoja1)

    hoja1 = weasyprint.HTML(string=hoja1_html)

    items_per_page = 12

    output_directory = os.path.join(settings.MEDIA_ROOT, str(request.user.id))
    os.makedirs(output_directory, exist_ok=True)

    pdf_files = []

    pdf_file_path = os.path.join(output_directory, 'page_0.pdf')
    pdf_files.append(pdf_file_path)
    hoja1.write_pdf(pdf_file_path)

    for i in range (0, len(items_prop), items_per_page):
        items_page = items_prop[i:i + items_per_page]
        print(items_page)
        context_hojax = {'articulos': items_page}

        hojax_template = get_template('email/pdf_resumen_hojax.html')
        hojax_html = hojax_template.render(context_hojax)

        hojax = weasyprint.HTML(string=hojax_html)

        pdf_file_path = os.path.join(output_directory, f'page_{(i // items_per_page) + 1}.pdf')
        pdf_files.append(pdf_file_path)
        hojax.write_pdf(pdf_file_path)

    file_name = f'resumen_negocio_bvi_{negocio.id_de_neg}.pdf'
    combined_pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
    merge_pdfs(pdf_files, combined_pdf_path)

    shutil.rmtree(output_directory)

    return combined_pdf_path, file_name

def consulta_pdf(context, request):
    """
    Descarga el archivo PDF en la computadora del usuario. El archivo se elimina dentro
    de la funcion. Retorna un HttpResonse que solo realiza la descarga sin renderizar
    nada en pantalla.
    """
    pdf_path, file_name = generar_pdf(context, request)

    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'filename={file_name}'

    return response

def get_pdf_path(context, request):
    """
    Genera y retorna el path del PDF generado. No elimina el archivo, pero se recomienda hacerlo
    posteriormente.
    """
    pdf_path, _ = generar_pdf(context, request)
    return pdf_path

def testeo(request):
    titulo = "Testeando email confirmacion"
    negocio = Negocio.objects.get(id_de_neg=2010)
    texto = "Buenos dias!"
    propuesta = Propuesta.objects.filter(negocio=negocio).last()
    items_prop = ItemPropuesta.objects.all().filter(propuesta=propuesta.id)
    observaciones = "estamos testeando"
    protocol = "https://"
    domain = Site.objects.get_current().domain
    full_negociacion_url =  protocol + domain + reverse('negocio', args=[negocio.id_de_neg,])
    recipient_list = [settings.TEMP_TO_EMAIL]
    context = {'titulo': titulo, 'texto': texto, 'obs': observaciones, 'url': full_negociacion_url, 'articulos': items_prop, 'prop': propuesta, 'negocio': negocio}
    template = "negocio"

    # return consulta_pdf(context, request)

    pdf_path = get_pdf_path(context, request)

    email_send("Testeando", recipient_list, f'email/{template}.txt', f'email/{template}.html', context, pdf_path)

    return render(request, f'email/crear_negocio.html', context)

def cliente(request):
    return render(request, 'cliente.html')

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    

    loginSuccess = True

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            next_url = request.POST['next']
            print(next_url)
            if next_url:
                return redirect(next_url)

            return redirect('inicio')
        else:
            loginSuccess = False
    
    context = {'loginSuccess' : loginSuccess}
    
    return render(request, 'login.html', context)


def estadoNegocio(negocio):
    return negocio.estado

def getNegociosToList(negocio):
    lista_negocios = []
    if (len(negocio) > 0):
        for a in negocio:
            propuesta = list(Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id','envio_comprador')[:1])
            if (not propuesta):
                pass
            else:
                id_prop = propuesta[0][0]
                envio = propuesta[0][1]
                a.id_prop = id_prop
                lista_negocios.append(a)
    return lista_negocios

def detalleAlerta(request):
    if request.method == 'POST':
        negocios = Negocio.objects.all().order_by('-timestamp')
        negocio = getNegociosToList(negocios)
        return render(request, 'modalAlerta.html', {'negocios':list(negocio)})    


def detalleNegocio(request):
    if request.method == 'POST':
        idProp = request.POST['idProp']        
        propuesta = Propuesta.objects.get(id=idProp)
        negocio = Negocio.objects.get(id=propuesta.negocio.id)
        grupo_activo = request.user.clase
        resultado = estadoNegocio(negocio)
        items = None
        persona = request.user
        if (grupo_activo == 'Logistica'):
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, empresa__id=persona.empresa.id)
        elif (grupo_activo == 'Administrador'):
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, empresa__id=persona.empresa.id)
        elif (grupo_activo == 'Proveedor'):
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, proveedor__id=persona.id) 
        else:
            items = ItemPropuesta.objects.filter(propuesta__id = idProp) 
            facturas = Factura.objects.filter(negocio=propuesta.negocio)
            remitos = Remito.objects.filter(negocio=propuesta.negocio)
            ordenesDeCompra = OrdenDeCompra.objects.filter(negocio=negocio)
            ordenesDePago = OrdenDePago.objects.filter(negocio=negocio)
            constancias = ConstanciaRentencion.objects.filter(negocio=negocio)
            recibos = Recibo.objects.filter(negocio=negocio)
            cheques = Cheque.objects.filter(negocio=negocio)
            cuentasCorriente = CuentaCorriente.objects.filter(negocio=negocio)
            facturasComision = FacturaComision.objects.filter(negocio=negocio)
            notas = Nota.objects.filter(negocio=negocio)

            comprobantes = {
                "facturas": facturas,
                "remitos": remitos,
                "ordenesDeCompra": ordenesDeCompra,
                "ordenesDePago": ordenesDePago,
                "constancias": constancias,
                "recibos": recibos,
                "cheques": cheques,
                "cuentasCorriente": cuentasCorriente,
                "facturasComision": facturasComision,
                "notas": notas,          
            }   
        return render (request, 'modalDetalleNegocio.html', {'negocio':negocio,'resultado':resultado, 'items':list(items), "comprobantes":comprobantes,})
    return render (request, 'modalDetalleNegocio.html')


def detalleItem(request):
    if request.method == 'POST':
        idItem = request.POST['idItem']        
        item = ItemPropuesta.objects.get(id = idItem)
        today = datetime.today()
        fechaEntrega = datetime.strptime(item.fecha_entrega, "%d/%m/%Y")
        resultado = calcularVencAtr(fechaEntrega, today)
        logistica = "Atrasado"
        if (item.fecha_real_entrega is not None):
            logistica = "Entregado"
        else:
            if (not resultado):
                if (item.fecha_salida_entrega is None):                    
                    logistica = "A Tiempo"
                else:                    
                    logistica = "En Tránsito"
        """
        diaA = int(d1[0:2])
        mesA = int(d1[3:5])
        añoA = int(d1[6:10])
        diaP = int(item.fecha_pago[0:2])
        mesP = int(item.fecha_pago[3:5])
        añoP = int(item.fecha_pago[6:10])
        difD = (diaP - diaA)
        difM = (mesP - mesA)
        difA = (añoP - añoA)
        proxMes = (diaP + 30 - diaA)
        estado_pago = "Pago Realizado"
        if (item.fecha_real_pago is None):
            if ((mesA == 12 and mesP == 1) and (difA == 1)):
                difM = 1
            if ((difA < 0) or (difM < 0 and difA == 0) or ((((diaP > diaA) and (mesP < mesA)) or ((diaP < diaA) and (mesP == mesA))))):
                estado_pago = "Atrasado" 
            elif ((diaP==diaA) and (mesP==mesA) and (añoP==añoA)):
                estado_pago = "Vence esta Semana"
            elif (((mesP == mesA) and (difD < 8 and difD > 0)) or ((difM == 1) and ((proxMes < 8 and proxMes > 0) and (diaP < 7)))):
                estado_pago = "Vence esta Semana"
            else:
                estado_pago = "Vencimiento Futuro"
        """
        estado_pago = "Pago Realizado"
        if (item.fecha_real_pago is None):                
            date_time_obj = datetime.strptime(item.fecha_pago, "%d/%m/%Y")
            if (date_time_obj < today):
                estado_pago = "Atrasado" 
            else:
                difDias = (today - date_time_obj).days                        
                if ((difDias * (-1)) <= 7):
                    estado_pago = "Vence esta Semana"
                else:
                    estado_pago = "Vencimiento Futuro"
        return render (request, 'modalDetalleItem.html', {'item':item, 'logistica':logistica, 'estado_pago':estado_pago})
    return render (request, 'modalDetalleItem.html')

def sendAlertaModal(request):
    data = {
        'result' : 'Error, la operacion fracasó.',
        'estado': False
    }
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descri = request.POST['descri']
        categoria = request.POST['categoria']
        ourid = request.POST['jsonText']
        ourid2 = ourid.replace('"', '')
        if (len(ourid2) <= 2):
            data = {
                'result' : 'Error! No ha seleccionado ningún Negocio!',
                'estado': False
            }
            return JsonResponse(data)
        id_carga = ""
        for a in range(len(ourid2)):
            if (ourid2[a] == "["):
                pass
            elif (ourid2[a] == "]"):
                negocio = Negocio.objects.get(id=int(id_carga))
                user = negocio.comprador
                notif = Notificacion(
                    titulo=titulo,
                    descripcion = descri,
                    categoria=categoria,
                    hyperlink=reverse('negocio', args=[negocio.id_de_neg,]),
                    user=user)
                notif.save()
            elif (ourid2[a] != ","):
                id_carga += str(ourid2[a])
            else:    
                negocio = Negocio.objects.get(id=int(id_carga))
                user = negocio.comprador
                notif = Notificacion(
                    titulo=titulo,
                    descripcion = descri,
                    categoria=categoria,
                    hyperlink=reverse('negocio', args=[negocio.id_de_neg,]),
                    user=user)
                notif.save()
                id_carga = ""
        data = {
            'result' : 'Alerta/s Enviada/s con éxito.',
            'estado': True
        }
        return JsonResponse(data)
    return JsonResponse(data)

class carga_excel(View):    
    def get(self, request):    
        return render(request, 'carga_excel.html')
    
    def post(self, request):
        try:
            excel_data = sheet_reader(request.FILES["myfile"])
        except MultiValueDictKeyError:
            excel_data = ["Seleccione un archivo"]
        except BadZipFile:
            excel_data = ["El archivo seleccionado es incorrecto"]

        return render(request, 'carga_excel.html', {'excel_data':excel_data})

def descarga_db_excel(request):
    response = sheet_writer()
    return response

def crear_negocio(request, comprador, vendedor, isComprador, observacion):
    created_by = None
    vendedor_obj = MyUser.objects.get(email=vendedor)
    comprador_obj = MyUser.objects.get(email=comprador)
    if isComprador:
        comprador_obj = request.user
        created_by = request.user.get_full_name()
        negocio = Negocio(
            comprador = comprador_obj,
            vendedor = vendedor_obj,
            estado = "RECIBIDO"
            )
        negocio.save()
    else:
        vendedor_obj = request.user
        created_by = request.user.get_full_name()
        negocio = Negocio(
            comprador = comprador_obj,
            vendedor = vendedor_obj,
            estado = "NEGOCIACION"
            )
        negocio.save()

    # NOTE: se manda email de confirmacion solo para usuario TEMP_TO_EMAIL a pedido del cliente
    email_vendedor = vendedor_obj.email
    email_comprador = comprador_obj.email
    match_vendedor = email_vendedor == settings.TEMP_TO_EMAIL
    match_comprador = email_comprador == settings.TEMP_TO_EMAIL
    if match_vendedor or match_comprador:
        subject = "Se creó un nuevo negocio"
        texto = f"""
        El nuevo negocio tiene identificador {negocio.get_id_de_neg()} y fue creado por {created_by}.
        Hacé click en el botón de abajo para ver el nuevo negocio.
        """
        protocol = "https://"
        domain = Site.objects.get_current().domain
        full_negociacion_url =  protocol + domain + reverse('negocio', args=[negocio.id_de_neg,])
        # recipient_list = [negocio.vendedor.email, negocio.comprador.email]
        recipient_list = [settings.TEMP_TO_EMAIL]
        context = {'titulo': subject, 'color': "", 'texto': texto, 'obs': observacion, 'url': full_negociacion_url, 'negocio': negocio}

        html_path = 'email/negocio.html' if negocio.is_confirmado() else 'email/crear_negocio.html'
        txt_path = 'email/negocio.txt' if negocio.is_confirmado() else 'email/crear_negocio.txt'

        email_send(subject, recipient_list, txt_path, html_path, context)

    return negocio
    

def crear_propuesta(negocio,observacion,isComprador):
    propuesta = Propuesta(
        negocio=negocio,
        observaciones=observacion,
        timestamp=timezone.localtime(),
        envio_comprador=isComprador,
        visto=isComprador,
        )    
    propuesta.save()
    return propuesta

class APIComprador(View):
    def get(self,request):
        compradores = []
        for comp in MyUser.objects.filter(clase='Comprador'):
            tmp = {
                'email':comp.email,
                'usuario':comp.get_full_name(),
                'empresa':comp.empresa.razon_social
            }
            compradores.append(tmp)
        return JsonResponse(list(compradores), safe=False)

class APIVendedor(View):
    def get(self,request):
        vendedores = []
        for vend in MyUser.objects.filter(clase='Vendedor'): 
            tmp = {
                'email': vend.email,
                'usuario': vend.get_full_name()
            }
            vendedores.append(tmp)
        return JsonResponse(list(vendedores), safe=False)


class APIDistribuidor(View):
    def get(self,request):
        proveedores = []
        for pro in MyUser.objects.filter(clase='Proveedor'):
            tmp = {
                'nombre':pro.get_full_name(),
                'email':pro.email
            }
            proveedores.append(tmp)
        return JsonResponse(list(proveedores), safe=False)

class APIEmpresa(View):
    def get(self,request):
        empresas = []
        for empresa in Empresa.objects.all().values("id"):
            try:
                emp = Empresa.objects.filter(id=empresa['id']).values("id")[0]['id']
            except Exception:
                context = Empresa.objects.none()
            tmp = {
                'empresa':Empresa.objects.filter(id=emp).values("razon_social")[0]['razon_social']            
                }
            empresas.append(tmp)
            
        return JsonResponse(list(empresas), safe=False)        

def filterArticulo(request, word):
    if word == 'undefined':
        empresas = Articulo.objects.values("empresa__nombre_comercial", "ingrediente", "marca", "id").order_by("ingrediente")
    else:
        empresas = Articulo.objects.filter(ingrediente=word).values("empresa__nombre_comercial", "ingrediente", "marca", "id").order_by("ingrediente")
    return JsonResponse(list(empresas), safe=False)

class ListArticuloView(View):
    def get(self, request, *args, **kwargs):
        all_articulos = Articulo.objects.all()
        return render(request, 'consultar_articulo.html', {'articulos':all_articulos})    

class ArticuloView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": ArticuloForm()}
        if ("pk" in kwargs):
            context["articulo"] = Articulo.objects.get(pk=kwargs["pk"])
            context["form"] = ArticuloForm(instance=context["articulo"])
        return render(request, 'articulo.html', context)

    def post(self, request, *args, **kwargs):
        articulo = None
        if ("pk" in kwargs):
            articulo = Articulo.objects.get(pk=kwargs["pk"])
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            articulo = form.save()
            return redirect('articulo', pk=articulo.pk)
        return render(request, 'articulo.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        articulo = Articulo.objects.get(pk=kwargs["pk"])
        articulo.delete()
        return HttpResponse(code=200)


class ListPresupuestoView(View):
    def get(self, request, *args, **kwargs):
        all_presupuestos = Presupuesto.objects.all()
        return render(request, 'consultar_presupuestos.html', {'presupuestos':all_presupuestos})    


class PresupuestoView(View):

    def get(self, request, *args, **kwargs):
        context = {
        "form": PresupuestoForm()}
        if ("pk" in kwargs):
            context["presupuesto"] = Presupuesto.objects.get(pk=kwargs["pk"])
            context["form"] = PresupuestoForm(instance=context["presupuesto"])
        return render(request, 'presupuesto.html', context)

    def post(self, request, *args, **kwargs):
        presupuesto = None
        if ("pk" in kwargs):
            presupuesto = Presupuesto.objects.get(pk=kwargs["pk"])
        form = PresupuestoForm(request.POST, instance=presupuesto)
        if form.is_valid():
            presupuesto = form.save()
            return redirect('presupuesto', pk=presupuesto.pk)
        return render(request, 'presupuesto.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        presupuesto = Presupuesto.objects.get(pk=kwargs["pk"])
        presupuesto.delete()
        return HttpResponse(code=200)

class NegocioView(View):
    def get(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, id_de_neg=kwargs["id_de_neg"])

        if not negocio.vendedor == request.user and not negocio.comprador == request.user:
            return redirect('home')

        data = negocio.propuestas.last()
        last = {
            'items': [],
            'observaciones': data.observaciones
        }
        comp = (request.user.clase == 'Comprador')
        if (comp==data.envio_comprador):
            data.visto = True
            data.save()
        for i in data.items.all():
            art = {}
            for f in i._meta.get_fields():
                val = getattr(i,f.name)
                if (f.is_relation and val):
                    art[f.name] = val.id
                else:
                    art[f.name] = val
                if (f.name == "precio_venta" or f.name == "precio_compra"):
                    art[f.name] = to_input_string(val)
                    
            last['items'].append(art)
        context = {
            "negocio": negocio,
            "propuestas": reversed(negocio.propuestas.all().reverse()),
            "last": json.dumps(last,cls=DjangoJSONEncoder),
            "divisas": DIVISA_CHOICES,
            'tasas': TASA_CHOICES,
            "distribuidores": MyUser.objects.filter(clase='Proveedor'),
            "tipo_pagos": TipoPago.objects.all(),
            "arts": Articulo.objects.all(),
            "items_count": ItemPropuesta.objects.filter(propuesta=data).count()
        }
        return render(request, 'negocio.html', context)

    def post(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, id_de_neg=kwargs["id_de_neg"])
        data = json.loads(request.body)
        isSend = bool(data["issend"])
        completed = True
        observaciones = "No hay observaciones" if not data["observaciones"] else data["observaciones"]
        envio_comprador = request.user.clase == 'Comprador'
        with transaction.atomic():
            prop = Propuesta(
                negocio=negocio,
                observaciones=data["observaciones"],
                envio_comprador=envio_comprador
            )
            prop.save()
            for item in data["items"]:
                tmp = ItemPropuesta()
                for f in tmp._meta.get_fields():
                    key = f.name
                    if key=="propuesta" or key=="id" or key == "isNew":
                        continue
                    is_new = item["isNew"]
                    value = item[key]
                    if key == "proveedor" and value == None:
                        setattr(tmp, key, None)
                    if f.is_relation and not (key == "proveedor" and value == None):
                        if key == "articulo" and envio_comprador and is_new:
                            art = Articulo.objects.get(pk=value)
                            try:
                                obj = Articulo.objects.get(ingrediente=art.ingrediente, empresa=None)
                            except:
                                obj = Articulo(ingrediente=art.ingrediente, empresa=None)
                                obj.save()
                        else:
                            obj = get_object_or_404(
                                f.related_model,
                                pk=value
                            )
                        setattr(tmp, key, obj)
                    else:
                        setattr(
                            tmp, 
                            key, 
                            value
                        )
                tmp.propuesta = prop
                tmp.save()
                completed &= tmp.aceptado

        titulo = "Presupuesto de {} {}".format(
            request.user.get_full_name(),
            "finalizado" if completed else "actualizado"
        )
        categoria = "Presupuesto {}".format(
            "finalizado" if completed else "actualizado"
        )
        user = None
        if prop.envio_comprador:
            user=negocio.comprador
        else:
            user=negocio.vendedor
        notif = Notificacion(
            titulo=titulo,
            categoria=categoria,
            hyperlink=reverse('negocio', args=[negocio.id_de_neg,]),
            user=user
        )
        notif.save()

        propuesta = Propuesta.objects.filter(negocio=negocio).last()
        itemsProp = ItemPropuesta.objects.all().filter(propuesta=propuesta.id)
        acc = []
        
        for i in itemsProp:
            acc.append(i.aceptado)
        
        if all(acc) and not itemsProp.count() == 0:
            if negocio.is_esp_conf() and not envio_comprador and not isSend:
                negocio.estado = "CONFIRMADO"
                negocio.fecha_cierre = timezone.localtime()
            elif not negocio.is_esp_conf() and not negocio.is_confirmado():
                if envio_comprador:
                    negocio.estado = "ESP_CONF"
                    titulo = "Negocio pendiente de confirmación"
                    categoria = "Presupuesto"
                    user = negocio.vendedor
                    notif = Notificacion(
                        titulo=titulo,
                        categoria=categoria,
                        hyperlink=reverse('negocio', args=[negocio.id_de_neg,]),
                        user=user
                    )
                    notif.save()
                else:
                    negocio.estado = "CONFIRMADO"
                    negocio.fecha_cierre = timezone.localtime()
            elif negocio.is_confirmado():
                negocio.estado = "YA_CONFIRMADO"
                
        negocio.save()

        if len(data.get('items')) == 0:
            negocio.estado = "CANCELADO"
            negocio.fecha_cierre = timezone.localtime()

        # send email

        formatted_fecha_cierre = ""
        texto = ""
        negocio_update = False

        fecha_cierre = negocio.fecha_cierre
        if fecha_cierre is not None:
            fecha = formats.date_format(fecha_cierre, "SHORT_DATE_FORMAT")
            hora = formats.time_format(fecha_cierre, "TIME_FORMAT")
            formatted_fecha_cierre = f"{fecha} a las {hora} hs"

        pre_titulo = f"Presupuesto de {request.user.get_full_name()}"
        pre_text = f"El presupuesto del negocio {negocio.get_id_de_neg()} ha sido"
        pos_text = "Hacé click en el botón de abajo para ver el historial de la negociación."
        pos_cierre_text = f"El negocio cerró el día {formatted_fecha_cierre}."

        if negocio.is_ya_confirmado():
            titulo = f"El presupuesto confirmado de {request.user.get_full_name()} ha sido modificado"
            texto = f"""
            El negocio que cerró el día {formatted_fecha_cierre} fue modificado.
            {pos_text}
            """
        elif negocio.is_confirmado():
            titulo = f"{pre_titulo} confirmado"
            texto = f"""
            {pre_text} confirmado. {pos_cierre_text}
            {pos_text}
            """
        elif negocio.is_cancelado():
            titulo = f"{pre_titulo} cancelado"
            texto = f"""
            {pre_text} cancelado. {pos_cierre_text}
            {pos_text}
            """
        elif negocio.is_esp_conf() and envio_comprador:
            titulo = f"{pre_titulo} actualizado. El cliente está esperando tu confirmación"
            texto = f"""
            {pre_text} actualizado.
            Hacé click en el botón de abajo para ver el historial de la negociación y confirmar el
            negocio en caso haber concluido la negocación.
            """
        else:
            negocio_update = True

        if not negocio_update:
            # NOTE: se manda email de confirmacion solo para usuario TEMP_TO_EMAIL a pedido del cliente
            email_vendedor = negocio.vendedor.email
            email_comprador = negocio.comprador.email
            match_vendedor = email_vendedor == settings.TEMP_TO_EMAIL
            match_comprador = email_comprador == settings.TEMP_TO_EMAIL
            if match_vendedor or match_comprador:
                protocol = "https://"
                domain = Site.objects.get_current().domain
                full_negociacion_url =  protocol + domain + reverse('negocio', args=[negocio.id_de_neg,])
                # recipient_list = [negocio.vendedor.email] if envio_comprador else [negocio.comprador.email]
                recipient_list = [settings.TEMP_TO_EMAIL]
                context = {'titulo': titulo, 'texto': texto, 'obs': observaciones, 'url': full_negociacion_url, 'articulos': itemsProp, 'prop': propuesta, 'negocio': negocio}
                html_path = 'email/negocio.html' if negocio.is_confirmado() else 'email/crear_negocio.html'
                txt_path = 'email/negocio.txt' if negocio.is_confirmado() else 'email/crear_negocio.txt'
                pdf_path = get_pdf_path(context, request)
                email_send(categoria, recipient_list, txt_path, html_path, context, pdf_path)
                os.unlink(pdf_path)
        else:
            if not negocio.is_esp_conf():
                if envio_comprador:
                    negocio.estado = "RECIBIDO"
                else:
                    negocio.estado = "NEGOCIACION"
                negocio.save()
            elif negocio.is_esp_conf() and not envio_comprador and isSend:
                negocio.estado = "NEGOCIACION"
                negocio.save()
                
        
        return redirect(reverse('negocio', kwargs={'id_de_neg': negocio.id_de_neg}))

class ListEmpresaView(View):
    def get(self, request, *args, **kwargs):
        all_empresas = Empresa.objects.all()
        return render(request, 'consultar_empresa.html', 
            {'empresas':all_empresas})


class EmpresaView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": EmpresaForm()}
        if ("pk" in kwargs):
            context["empresa"] = Empresa.objects.get(pk=kwargs["pk"])
            context["form"] = EmpresaForm(instance=context["empresa"])
        return render(request, 'empresa.html', context)

    def post(self, request, *args, **kwargs):
        empresa = None
        if ("pk" in kwargs):
            empresa = Empresa.objects.get(pk=kwargs["pk"])
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            empresa = form.save()
            return redirect('empresa', pk=empresa.pk)
        return render(request, 'empresa.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        empresa = Empresa.objects.get(pk=kwargs["pk"])
        empresa.delete()
        return HttpResponse(code=200)


def cargarListasNegociosAbiertos(negocioFilter, tipo):
    lista_negocios = []
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp','envio_comprador')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            envio = propuesta[0][2]
            if (envio == tipo):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
                comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
                lista = {
                    'fecha':fecha_p,
                    'items':list(items),
                    'comprador': comprador,
                    'empresa':negocio.comprador.empresa.razon_social
                }
                lista_negocios.append(lista)
            else:
                pass
    return lista_negocios

def cargarListasNegociosCerrados(negocioFilter):
    lista_negocios = []
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
            comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
            lista = {
                'fecha':fecha_p,
                'items':list(items),
                'comprador': comprador,
                'empresa':negocio.comprador.empresa.razon_social
            }
            lista_negocios.append(lista)
    return lista_negocios

def removeDuplicates(arr):
    new_arr = list()
    new_arr.append(arr[0].id)
    for i in range(1, len(arr)):
        if (arr[i].ingrediente != arr[i-1].ingrediente):
            new_arr.append(arr[i].id)
    return new_arr

class APIArticulos(View):
    def get(self, request):
        articulos = Articulo.objects.all().order_by('ingrediente')
        # query = removeDuplicates(list(articulos))
        # articulos = Articulo.objects.filter(pk__in=query).order_by('ingrediente')
        return JsonResponse(list(articulos.values("empresa__nombre_comercial", "ingrediente", "id", "marca")), safe=False)

    def post(self, request):
        recieved = json.loads(request.body.decode("utf-8"))
        observacion = recieved.get("observaciones")
        isComprador = recieved.get("envio_comprador")
        comprador = recieved.get("comprador")
        vendedor = recieved.get("vendedor")
        negocio = crear_negocio(request, comprador, vendedor, isComprador, observacion)
        propuesta = crear_propuesta(negocio,observacion,isComprador)
        data = recieved.get("data")
        for i in range(len(data)):
            actual = data[i]
            empresa_nombre = actual.get("Empresa")
            ingrediente = actual.get("Ingrediente")
            distribuidor = actual.get("Distribuidor")
            domicilio = actual.get("Destino")
            tipo_pago_str = actual.get("Tipo de pago")
            divisa = actual.get("Divisa")
            # divisa = get_from_tuple(DIVISA_CHOICES,divisa_tmp)
            
            if not actual.get("Tasa"):
                tasa = 0
            else:
                tasa = Decimal(actual.get("Tasa"))
            # tasa = get_from_tuple(TASA_CHOICES,tasa_tmp)

            if not empresa_nombre:
                empresa = None
                try:
                    articulo = Articulo.objects.get(ingrediente=ingrediente, empresa=empresa)
                except:
                    articulo = Articulo(ingrediente=ingrediente, empresa=empresa)
                    articulo.save()
            else:
                empresa = Empresa.objects.get(nombre_comercial=empresa_nombre)
                articulo = Articulo.objects.get(ingrediente=ingrediente, empresa=empresa)
            # try:
            #     domicilio = Domicilio.objects.get(direccion=domicilio_str)
            # except ObjectDoesNotExist:
            #     domicilio = Domicilio(direccion=domicilio_str)
            #     domicilio.save()

            if isComprador:
                proveedor = None
            else:
                proveedor = MyUser.objects.get(email=distribuidor)

            #traer el objecto tipo de pago
            if len(actual.get("Tipo de pago").strip()) != 0:
                tipo_pago = TipoPago.objects.get(nombre=tipo_pago_str)
            else:
                tipo_pago = None

            precio_venta = actual.get("Precio venta")
            precio_compra = actual.get("Precio compra")

            if isComprador:
                precio_compra = 0.0
            
            item = ItemPropuesta(
                articulo=articulo, 
                proveedor=proveedor,
                propuesta=propuesta,
                precio_venta=precio_venta,
                precio_compra=precio_compra,
                cantidad=actual.get("Cantidad"),
                divisa=divisa,
                tipo_pago=tipo_pago,
                tasa=tasa,
                destino=domicilio,
                aceptado=False,
                fecha_pago=actual.get("Fecha de pago"),
                fecha_entrega=actual.get("Fecha de entrega"),)
            item.save()
        return JsonResponse(negocio.id_de_neg, safe=False)

def getPagos(request):
    tipo_pago = TipoPago.objects.all().values("nombre")
    return JsonResponse(list(tipo_pago), safe=False)

def get_from_tuple(my_tuple, value):
    ret = ""
    for (x,y) in my_tuple:
        if y==value:
            ret = x
    return ret

def successPassword(request):
    return render(request, 'tempAux/successPass.html')

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordsChangingForm

    def get_success_url(self):
        return reverse('successPassword')

def selecNegComprobante(request, *args, **kwargs):
    if request.method == 'POST':
        negocios = Negocio.objects.all().order_by('-timestamp')
        negocio = getNegociosToList(negocios)
        tipoN = kwargs["tipo"]
        tipo = comprobanteTipo(tipoN)        
        context = {
            'tipoN': tipoN,
            'tipo': tipo,
            'negocios':list(negocio),
        }
        return render(request, 'modalSelecNeg.html', context)

def formFactura(request, *args, **kwargs):
    if request.method == 'POST':
        form = FacturaForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = FacturaForm(initial = {'negocio': negocio})
        else:
            form = FacturaForm()
        tipo = "Factura"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formRemito(request, *args, **kwargs):
    if request.method == 'POST':
        form = RemitoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = RemitoForm(initial = {'negocio': negocio})
        else:
            form = RemitoForm()
        tipo = "Remito"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formOrdenDeCompra(request, *args, **kwargs):
    if request.method == 'POST':
        form = OrdenDeCompraForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = OrdenDeCompraForm(initial = {'negocio': negocio})
        else:
            form = OrdenDeCompraForm()
        tipo = "OrdenDeCompra"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formOrdenDePago(request, *args, **kwargs):
    if request.method == 'POST':
        form = OrdenDePagoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = OrdenDePagoForm(initial = {'negocio': negocio})
        else:
            form = OrdenDePagoForm()
        tipo = "OrdenDePago"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formConstanciaRentencion(request, *args, **kwargs):
    if request.method == 'POST':
        form = ConstanciaRentencionForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = ConstanciaRentencionForm(initial = {'negocio': negocio})
        else:
            form = ConstanciaRentencionForm()
        tipo = "ConstanciaRentencion"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formRecibo(request, *args, **kwargs):
    if request.method == 'POST':
        form = ReciboForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = ReciboForm(initial = {'negocio': negocio})
        else:
            form = ReciboForm()
        tipo = "Recibo"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formCheque(request, *args, **kwargs):
    if request.method == 'POST':
        form = ChequesForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = ChequesForm(initial = {'negocio': negocio})
        else:
            form = ChequesForm()
        tipo = "Cheque"
        context = {
            'form':form,
            'tipo':tipo,
            }
        return render(request, 'modalForm.html', context)


def formCuentaCorriente(request, *args, **kwargs):
    if request.method == 'POST':
        form = CuentaCorrientesForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = CuentaCorrientesForm(initial = {'negocio': negocio})
        else:
            form = CuentaCorrientesForm()
        tipo = "CuentaCorrientes"
        context = {
        'form':form,
        'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formFacturaComision(request, *args, **kwargs):
    if request.method == 'POST':
        form = FacturaComisionesForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = FacturaComisionesForm(initial = {'negocio': negocio})
        else:
            form = FacturaComisionesForm()
        tipo = "FacturaComisiones"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)

def formNota(request, *args, **kwargs):
    if request.method == 'POST':
        form = NotaForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            documento = request.FILES['documento']
            form.documento = (documento.name,documento)
            instance = form.save()
            return redirect("home")
            return HttpResponse("Carga Exitosa")
        else:
            print(form.errors)  
        return redirect("home")
    else:
        if ("neg" in kwargs):
            negocio = Negocio.objects.get(id=kwargs["neg"])
            form = NotaForm(initial = {'negocio': negocio})
        else:
            form = NotaForm()
        tipo = "Nota"
        context = {
            'form':form,
            'tipo':tipo
        }
        return render(request, 'modalForm.html', context)