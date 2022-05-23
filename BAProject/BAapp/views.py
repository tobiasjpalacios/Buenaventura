import json
from zipfile import BadZipFile

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordChangeView, redirect_to_login
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.core import serializers
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.dateparse import parse_date
from .forms import *
from .models import *
from .choices import DIVISA_CHOICES, TASA_CHOICES, TIPO_DE_NEGOCIO_CHOICES
from .scriptModels import *
from .decorators import *
from datetime import date, datetime, timedelta
from django.utils import formats
from BAapp.utils.utils import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from .utils.email_send import email_send
from django.contrib.sites.models import Site
import operator
from functools import reduce
from django.conf import settings


User = settings.AUTH_USER_MODEL

def cuentas(request):
    return render(request, 'cuentas.html')

def admin(request):
    return render(request,'admin.html')

def chat(request):
    return render(request,'chat.html')


# los nuevos views

class NuevoNegocioView(View):
    def get(self, request, *args, **kwargs):
        return render(request,'nuevo_negocio.html')

class TodoseNegociosView(View):
    def get(self, request, *args, **kwargs):
        grupo_activo = request.user.clase
        negocio = getNegociosByClase(request,grupo_activo,1)
        vendedor = MyUser.objects.filter(clase='Vendedor')
        return render(request, 'todos_los_negocios.html', {'todos_negocios':list(negocio), 'todos_vendedores':vendedor})  

class Info_negocioView(View): 
    def get(self, request, *args, **kwargs):
        if ("pk" in kwargs):
            idProp = kwargs["pk"]
            propuesta = Propuesta.objects.get(pk=kwargs["pk"])
            negocio = Negocio.objects.get(id=propuesta.negocio.id)
            grupo_activo = request.user.clase
            envio = propuesta.envio_comprador
            if (grupo_activo == 'Comprador' or grupo_activo == 'Gerente'):
                envio = not envio
            resultado = estadoNegocio(negocio.fecha_cierre, negocio.aprobado, envio)
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
            return render (request, 'info_negocio.html', {'negocio':negocio,'resultado':resultado, 'items':list(items), "comprobantes":comprobantes,})

class ComprobantesView(View):
    def get(self, request, *args, **kwargs):
        facturas = Factura.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(proveedor=request.user))
        remitos = Remito.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(proveedor=request.user))
        ordenesDeCompra = OrdenDeCompra.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
        ordenesDePago = OrdenDePago.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
        constancias = ConstanciaRentencion.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
        recibos = Recibo.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
        cheques = Cheque.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))
        cuentasCorriente = CuentaCorriente.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))
        facturasComision = FacturaComision.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user) | Q(recibe_proveedor=request.user))
        notas = Nota.objects.filter(Q(negocio__comprador=request.user) | Q(negocio__vendedor=request.user))

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
        
        return render(request, 'comprobantes.html',{"comprobantes":comprobantes})

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
    grupo_activo = request.user.clase
    #A = Administrador 
    if (grupo_activo == "Administrador"):
        negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=fcn, comprador__empresa=reques.user.empresa).values_list('id', flat=True).order_by('-timestamp').distinct())
    #C = Comprador
    elif (grupo_activo == "Comprador"):
        negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=fcn, comprador__id=request.user.id).values_list('id', flat=True).order_by('-timestamp').distinct())
    #V = Vendedor
    elif (grupo_activo == "Vendedor"):
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
        negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())    
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
            envio = propuesta[0][1]
            negocio.id_prop = id_prop
            grupo_activo = request.user.clase
            if (grupo_activo == 'Comprador' or grupo_activo == 'Gerente'):
                envio = not envio
            negocio.estado = estadoNegocio(negocio.fecha_cierre, negocio.aprobado, envio)
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
            negocios = Negocio.objects.all().order_by('-timestamp')
            negocio = getNegociosToList(negocios)
            for a in negocio:
                a.proveedores = getProveedoresNegocio(a)

    # Comprador
    elif (user_clase == 'Comprador'):
        if (tipo == 2):
            negocio = Negocio.objects.filter(comprador=request.user).order_by('-timestamp').values_list('id', flat=True)
        else:
            negocios = Negocio.objects.filter(comprador=request.user).order_by('-timestamp')
            negocio = getNegociosToList(negocios)
    
    # Gerente
    elif (user_clase == 'Gerente'):
        mi_gerente = request.user
        if (tipo == 2):
            negocio = Negocio.objects.filter(comprador__empresa__id=mi_gerente.empresa.id).order_by('-timestamp').values_list('id', flat=True)
        else:
            negocios = Negocio.objects.filter(comprador__empresa__id=mi_gerente.empresa.id).order_by('-timestamp')
            negocio = getNegociosToList(negocios)

    # proveedor
    elif (user_clase == 'Proveedor'):
        negocios = Negocio.objects.filter(fecha_cierre__isnull=False).order_by('-timestamp')
        lista_ids = []
        for a in negocios:
            empleadoP = Proveedor.objects.get(persona=request.user)
            id_prop = Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id', flat=True)[:1]
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop, proveedor__id=empleadoP.id)
            if (len(items) > 0):                
                lista_ids.append(a.id)
        if (tipo == 2):
            negocio = lista_ids
        else:
            negocios = Negocio.objects.filter(id__in=lista_ids).order_by('-timestamp')
            negocio = getNegociosToList(negocios)

    # administrador
    elif (user_clase == 'Administrador'):
        negocios = Negocio.objects.filter(comprador__empresa=reques.user.empresa).order_by('-timestamp')
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
            if (grupo_activo == 'Compradores' or grupo_activo == 'Gerentes'):
                envio = not envio
            a.id_prop = id_prop
            a.estado = estadoNegocio(a.fecha_cierre, a.aprobado, envio)
    for b in todos_negocios:        
        if (b.estado == estado):
            b.proveedores = getProveedoresNegocio(b)
            negocioAux.append(b)
    vendedores = MyUser.objects.filter(clase='Vendedor')   
    return render(request, 'todos_los_negocios.html', {'todos_negocios':list(negocioAux), 'todos_vendedores':vendedores})

def filtrarNegocios(request):
    data = []
    if (request.method == 'POST'):
        vendedor = request.POST['vendedor']
        estado = request.POST['estado']
        tipo = request.POST['tipo']
        tipoFecha = request.POST['tipoFecha']
        fechaD = request.POST['fechaDesde']
        fechaH = request.POST['fechaHasta']
        idDeNeg = request.POST['idDeNeg']
        error = False
        listaVendedor = []
        grupo_activo = request.user.clase
        negocios_permitidos = getNegociosByClase(request,grupo_activo,2)
        if (vendedor == "todos"):
            listaVendedor = Negocio.objects.filter(id__in=negocios_permitidos).values_list('id', flat=True)
        else:
            lista_ids = []
            id_carga = "" 
            ourid2 = vendedor.replace('"', '')
            for a in ourid2:
                if (a == '['):
                    pass
                elif (a == ']'):
                    lista_ids.append(int(id_carga))
                elif (a != ','):
                    id_carga += str(a)
                else:
                    lista_ids.append(int(id_carga))
                    id_carga = ""    
            listaVendedor = Negocio.objects.filter(vendedor__id__in = lista_ids,id__in=negocios_permitidos).values_list('id', flat=True)
        listaEstado = []
        if (estado == "todos"):
            listaEstado = Negocio.objects.filter(id__in=negocios_permitidos).values_list('id', flat=True)            
        else:
            todos_negocios = Negocio.objects.filter(id__in=negocios_permitidos)
            for a in todos_negocios:
                propuesta = list(Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id','envio_comprador')[:1])
                if (not propuesta):
                    pass
                else:
                    id_prop = propuesta[0][0]
                    envio = propuesta[0][1]
                    a.id_prop = id_prop
                    a.estado = estadoNegocio(a.fecha_cierre, a.aprobado, envio)
            for b in todos_negocios:
                if (b.estado in estado):
                    listaEstado.append(b.id)
        listaTipo = []
        if (tipo == "todos"):
            listaTipo = Negocio.objects.filter(id__in=negocios_permitidos).values_list('id', flat=True)
        else:
            listaTipo = Negocio.objects.filter(tipo_de_negocio = get_from_tuple(TIPO_DE_NEGOCIO_CHOICES, tipo),id__in=negocios_permitidos).values_list('id', flat=True)
        listaFecha = []
        if (int(tipoFecha) == 0):
            listaFecha = Negocio.objects.filter(id__in=negocios_permitidos).values_list('id', flat=True)
        else:
            fechaD = datetime.strptime(fechaD, "%d/%m/%Y")
            fechaH = datetime.strptime(fechaH, "%d/%m/%Y")
            # filtra las fechas correctamente pero no se cual es la diferencia entre tipoFecha 1 y 2
            if (int(tipoFecha) == 1):
                listaFecha = Negocio.objects.filter(timestamp__date__range=(fechaD, fechaH),id__in=negocios_permitidos).values_list('id', flat=True)
            else:
                listaFecha = Negocio.objects.filter(fecha_cierre__date__range=(fechaD, fechaH),id__in=negocios_permitidos).values_list('id', flat=True)
        listaIdDeNeg = []
        if idDeNeg is not None:
            if idDeNeg == "" or int(idDeNeg) <= 0:
                listaIdDeNeg = Negocio.objects.filter(id__in=negocios_permitidos).values_list('id', flat=True)
            else:
                listaIdDeNeg = Negocio.objects.filter(id__in=negocios_permitidos, id=idDeNeg).values_list('id', flat=True)
        listaVendedor = getIdsQuery(listaVendedor)
        listaEstado = getIdsQuery(listaEstado)
        listaTipo = getIdsQuery(listaTipo)         
        listaFecha = getIdsQuery(listaFecha)
        listaIdDeNeg = getIdsQuery(listaIdDeNeg)
        listaNeg = set(listaVendedor).intersection(listaEstado)
        listaNeg2 = set(listaNeg).intersection(listaTipo)
        listaNeg3 = set(listaNeg2).intersection(listaFecha)
        listaNeg4 = set(listaNeg3).intersection(listaIdDeNeg)
        todos_los_negocios = Negocio.objects.filter(id__in=list(listaNeg4)).order_by('-timestamp')
        for a in todos_los_negocios:
            propuesta = list(Propuesta.objects.filter(negocio__id = a.id).order_by('-timestamp').values_list('id','envio_comprador')[:1])
            if (not propuesta):
                pass
            else:
                id_prop = propuesta[0][0]
                envio = propuesta[0][1]
                a.id_prop = id_prop
                a.estado = estadoNegocio(a.fecha_cierre, a.aprobado, envio)
        grupo_activo = request.user.clase
        if (grupo_activo == 'Vendedor'):
            for a in todos_los_negocios:
                a.proveedores = getProveedoresNegocio(a)
    return render(request,'tempAux/tableNegociosFiltros.html',{'todos_negocios':todos_los_negocios} )
    
def getIdsQuery(lista):
    listaId = []
    for a in lista:
        listaId.append(a)
    return listaId

def getProveedoresNegocio(negocio):
    proveedores = []
    if (negocio.fecha_cierre is not None):
        items = ItemPropuesta.objects.filter(propuesta__negocio__id = negocio.id)
        proveedores = []
        id_proveedores = [] 
        for b in items:
            if (b.proveedor and b.proveedor.id not in id_proveedores):
                id_proveedores.append(b.proveedor.id)
                prov = b.proveedor.apellido + " " + b.proveedor.nombre  
                proveedores.append(prov)
    return proveedores

def testeo(request):

    neg = Negocio.objects.all()

    context = {
        'negAp': neg.filter(aprobado=True),
        'negNoAp': neg.filter(aprobado=False)
    }

    return render(request, 'testeo.html', context)

def cliente(request):
    return render(request, 'cliente.html')

def check_user_group_after_login(request):
    redirects = {
        'Administradores': redirect('vistaAdministrador'),
        'Compradores': redirect('vistaCliente'),
        'Gerentes': redirect('vistaGerente'),
        'Proveedores': redirect('vistaProveedor'),
        'Vendedores': redirect('vendedor'),
        'Logisticas': redirect('vistaLogistica')
    }

    return redirect('notificaciones')

def landing_page(request):
    if (request.user.is_authenticated):
        return (check_user_group_after_login(request))

    loginSuccess = True

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('router')
        else:
            loginSuccess = False
    
    context = {'loginSuccess' : loginSuccess}
    
    return render(request, 'Principal.html', context)

# ya no se usan creo

@group_required('Administradores')
def vistaAdministrador(request):
    mi_Administrador = Administrador.objects.get(persona__user=request.user)
    negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnr = listasNAA(request,negociosAbiertos, True)
    lnp = listasNAA(request,negociosAbiertos, False)
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnc = listaNCL(request,negociosCerrConf, 'A')
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, cancelado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnnc = listaNCL(request,negociosCerrRech, 'A')
    #Semaforo
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #Logistica
    lnl = listaNL(request,negociosCerrConf,'A')
    #lpn = Lista Presupuesto Notificaciones
    lpn = Notificacion.objects.filter(user=request.user, categoria__contains='Presupuesto').order_by('-timestamp')
    #lln = Lista Logistica Notificaciones
    lln = Notificacion.objects.filter(user=request.user, categoria__contains='Logistica').order_by('-timestamp')
    #lvn = Lista Vencimiento Notificaciones
    lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html', {'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'presupuestos_recibidos':list(lnr),'presupuestos_negociando':list(lnp),'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})

@group_required('Logisticas')
def vistaLogistica(request):
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnc = listaNCL(request,negociosCerrConf, 'L')
    lnl = listaNL(request,negociosCerrConf,'L')
    lista_ids = []
    # esto va comentado
    notis = Notificacion.objects.all()
    for a in notis:
        first = a.hyperlink.split("/",1)[1]
        idNegocio = first.split("/",1)[1]
        negocio = Negocio.objects.get(id=int(idNegocio)) 
        if (int(negocio.comprador.empresa.id) == int(mi_gerente.empresa.id)):
            lista_ids.append(a.id)   
    # hasta aca
    lpn = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Presupuesto').order_by('-timestamp')
    lln = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Logistica').order_by('-timestamp')
    lvn = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html',{'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'negocios_cerrados_confirmados':list(lnc)})

@group_required('Proveedores')
def vistaProveedor(request):
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnc = listaNCL(request,negociosCerrConf,'P')
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, cancelado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnnc = listaNCL(request,negociosCerrRech,'P')
    #Semaforo
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #Logistica
    lnl = listaNL(request,negociosCerrConf,'P')
    #Notificaciones
    lpn = Notificacion.objects.filter(user=request.user, categoria__contains='Presupuesto').order_by('-timestamp')
    lln = Notificacion.objects.filter(user=request.user, categoria__contains='Logistica').order_by('-timestamp')
    lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html', {'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})    

# creo que no se usan
@group_required('Gerente')
def vistaGerente(request):
    mi_gerente = Gerente.objects.get(persona__user=request.user)
    negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=True, comprador__empresa__id=mi_gerente.empresa.id).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnp = listasNA(negociosAbiertos, True)
    lnr = listasNA(negociosAbiertos, False)
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True, comprador__empresa__id=mi_gerente.empresa.id).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnc = listaNC(negociosCerrConf)
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, cancelado=True, comprador__empresa__id=mi_gerente.empresa.id).values_list('id', flat=True).order_by('-timestamp').distinct())
    lnnc = listaNC(negociosCerrRech)
    #Semaforo
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #Logistica
    lnl = listaNL(request,negociosCerrConf,'G')
    #Notificaciones
    notis = Notificacion.objects.all()
    lista_ids = []
    for a in notis:
        first = a.hyperlink.split("/",1)[1]
        idNegocio = first.split("/",1)[1]
        negocio = Negocio.objects.get(id=int(idNegocio)) 
        if (int(negocio.comprador.empresa.id) == int(mi_gerente.empresa.id)):
            lista_ids.append(a.id)   
    lpn = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Presupuesto').order_by('-timestamp')
    lln = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Logistica').order_by('-timestamp')
    lvn = Notificacion.objects.filter(id__in=lista_ids, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html', {'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'presupuestos_recibidos':list(lnr),'presupuestos_negociando':list(lnp),'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})    

@group_required('Compradores')
def vistaCliente(request):
    negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=True, comprador__user=request.user).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnp = listasNA(negociosAbiertos, True)
    lnr = listasNA(negociosAbiertos, False)
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True, comprador__user=request.user).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnc = listaNC(negociosCerrConf)
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, cancelado=True, comprador__user=request.user).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnnc = listaNC(negociosCerrRech)
    #Semaforo
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #Logistica
    lnl = listaNL(request,negociosCerrConf,'C')
    #lpn = Lista Presupuesto Notificaciones
    lpn = Notificacion.objects.filter(user=request.user, categoria__contains='Presupuesto').order_by('-timestamp')
    #lln = Lista Logistica Notificaciones
    lln = Notificacion.objects.filter(user=request.user, categoria__contains='Logistica').order_by('-timestamp')
    #lvn = Lista Vencimiento Notificaciones
    lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html', {'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'presupuestos_recibidos':list(lnr),'presupuestos_negociando':list(lnp),'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})    

@group_required('Vendedores')
def vendedor(request):
    #Negocios en Procesos
    negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnr = listasNA(negociosAbiertos, True)
    lnp = listasNA(negociosAbiertos, False)
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnc = listaNC(negociosCerrConf)
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, cancelado=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnnc = listaNC(negociosCerrRech)
    #Semaforo
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #Logistica
    lnl = listaNL(request,negociosCerrConf,'V')
    #lpn = Lista Presupuesto Notificaciones
    lpn = Notificacion.objects.filter(user=request.user, categoria__contains='Presupuesto').order_by('-timestamp')
    #lln = Lista Logistica Notificaciones
    lln = Notificacion.objects.filter(user=request.user, categoria__contains='Logistica').order_by('-timestamp')
    #lvn = Lista Vencimiento Notificaciones
    lvn = Notificacion.objects.filter(user=request.user, categoria__contains='Vencimiento').order_by('-timestamp')
    return render(request, 'vendedor.html', {'lista_vencimiento':lvn,'lista_logistica_noti':lln,'lista_presupuestos':lpn,'lista_logistica':lnl,'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'presupuestos_recibidos':list(lnr),'presupuestos_negociando':list(lnp),'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})


def estadoNegocio(fecha_cierre, aprobado, envio):
    if (fecha_cierre is None):
        if (envio):
            return "Recibido"
        else:
            return "En Negociación"
    else:
        if (aprobado):
            return "Confirmado"
    return "Cancelado"

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
                a.estado = estadoNegocio(a.fecha_cierre, a.aprobado, envio)
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
        envio = propuesta.envio_comprador
        if (grupo_activo == 'Comprador' or grupo_activo == 'Gerente'):
            envio = not envio
        resultado = estadoNegocio(negocio.fecha_cierre, negocio.aprobado, envio)
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


def listaNL(request,negocioFilter):
    lista_negocios = []
    en_tiempo = False
    en_transito = False
    entregado = False
    atrasado = False
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre        
            modulo = request.user.clase
            #P = Proveedor 4
            if (modulo == 'Proveedor'):    
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, proveedor__id=request.user.id)
            #L = Logistica 6
            elif (modulo == 'Logistica'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=request.user.id)
            #A = Administrador 1
            elif (modulo == 'Administrador'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=request.user.id)
            #C = Comprador 2
            elif (modulo == 'Comprador'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, propuesta__negocio__comprador__id=request.user.id)
            #V = Vendedor 3
            elif (modulo == 'Vendedor'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop)
            else:
                items = []
            
            
            if (items.count() < 1):
                pass
            else:
                destino = ""
                estado = ""
                destino_tiempo = ""
                fecha_tiempo = "00/00/0000"
                destino_transito = ""
                fecha_transito = "00/00/0000"
                destino_entregado = ""
                fecha_entregado = "00/00/0000"
                destino_atrasado = ""
                fecha_atrasado = "00/00/0000"
                primero_tiempo = True
                primero_transito = True
                primero_entregado = True
                primero_atrasado = True
                today = datetime.today()
                for b in items:
                    fechaEntrega = datetime.strptime(b.fecha_entrega, "%d/%m/%Y")
                    resultado = calcularVencAtr(fechaEntrega, today)
                    print (resultado)
                    if (b.fecha_real_entrega is not None):
                        #Entregado
                        entregado = True
                        if (primero_entregado):
                            fecha_entregado = b.fecha_entrega
                            destino_entregado = b.destino
                            primero_entregado = False
                        else:
                            fechaEntregado = datetime.strptime(fecha_entregado, "%d/%m/%Y")
                            res = calcularVencAtr(b.fecha_entrega, fecha_entregado)
                            if (not res):
                                fecha_entregado = b.fecha_entrega
                                destino_entregado = b.destino
                    else:
                        if (not resultado):
                            if (b.fecha_salida_entrega is None):
                                #A Tiempo
                                en_tiempo = True
                                if (primero_tiempo):
                                    fecha_tiempo = b.fecha_entrega
                                    destino_tiempo = b.destino
                                    primero_tiempo = False
                                else:
                                    fechaTiempo = datetime.strptime(fecha_tiempo, "%d/%m/%Y")
                                    res = calcularVencAtr(fechaEntrega, fechaTiempo)
                                    if (not res):
                                        fecha_tiempo = b.fecha_entrega
                                        destino_tiempo = b.destino
                            else:
                                #En Transito
                                en_transito = True
                                if (primero_transito):
                                    fecha_transito = b.fecha_entrega
                                    destino_transito = b.destino
                                    primero_transito = False
                                else:
                                    res = calcularVencAtr(b.fecha_entrega, fecha_transito)
                                    if (not res):
                                        fecha_transito = b.fecha_entrega
                                        destino_transito = b.destino
                        else:
                            #Atrasado
                            atrasado = True
                            if (primero_atrasado):
                                    fecha_atrasado = b.fecha_entrega    
                                    destino_atrasado = b.destino
                                    primero_atrasado = False
                            else:
                                fechaAtrasado = datetime.strptime(fecha_atrasado, "%d/%m/%Y")
                                res = calcularVencAtr(b.fecha_entrega, fecha_atrasado)
                                if (not res):
                                    fecha_atrasado = b.fecha_entrega
                                    destino_atrasado = b.destino
                if (atrasado):
                    estado = "Atrasado"
                    destino = destino_atrasado
                    fecha = fecha_atrasado
                elif (en_tiempo):
                    estado = "A Tiempo"
                    destino = destino_tiempo
                    fecha = fecha_tiempo
                elif (en_transito):
                    estado = "En Tránsito"
                    destino = destino_transito
                    fecha = fecha_transito
                else:
                    estado = "Entregado"
                    destino = destino_entregado
                    fecha = fecha_entregado      
                lista = {
                    'fecha':fecha,
                    'destinatario': comprador,
                    'destino': destino,
                    'id_prop':id_prop,
                    'empresa':negocio.comprador.empresa.razon_social,
                    'estado':estado
                }
                lista_negocios.append(lista)
                en_tiempo = False
                en_transito = False
                entregado = False
                atrasado = False
    return lista_negocios


def detalleLogistica(request):
    if request.method == 'POST':
        idProp = request.POST['idProp']
        propuesta = Propuesta.objects.get(id = idProp)
        negocio = Negocio.objects.get(id=propuesta.negocio.id)
        negocio.fecha_aux = propuesta.timestamp
        cliente = None
        proveedores = None
        grupo_activo = request.user.clase
        items = None
        if (grupo_activo == 'Logistica'):
            persona = Persona.objects.get(user=request.user)
            empleadoL = Logistica.objects.get(persona__id=persona.id)
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, empresa__id=empleadoL.empresa.id)
        elif (grupo_activo == 'Administrador'):
            persona = Persona.objects.get(user=request.user)
            administradorL = Administrador.objects.get(persona__id=persona.id)
            items = ItemPropuesta.objects.filter(propuesta__id = idProp,empresa__id=administradorL.empresa.id)
        elif (grupo_activo == 'Proveedor'):
            persona = Persona.objects.get(user=request.user)
            proveedorP = Proveedor.objects.get(persona__id=persona.id)
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, proveedor__id=proveedorP.id)        
        else:
            items = ItemPropuesta.objects.filter(propuesta__id = idProp)
            cliente = negocio.comprador
            lista_ids = []
            for a in items:
                if (a.proveedor.id in lista_ids):
                    pass
                else:
                    lista_ids.append(a.proveedor.id)
            proveedores = Proveedor.objects.filter(id__in=lista_ids) 
        today = datetime.today()
        for b in items:
            b.estados = ('Atrasado', 'A Tiempo', 'Entregado', 'Aceptado')
            fechaEntrega = datetime.strptime(b.fecha_entrega, "%d/%m/%Y")
            resultado = calcularVencAtr(fechaEntrega, today)
            if (b.fecha_real_entrega is not None):
                #Entregado
                b.estado = 'Entregado'
                b.estados = ('Atrasado', 'A Tiempo', 'En Tránsito')
            else:
                if (not resultado):
                    if (b.fecha_salida_entrega is None):
                        #A Tiempo
                        b.estado = 'A Tiempo'
                        b.estados = ('Transito', 'Entregado','Atrasado')
                        
                    else:
                        #En Transito
                        b.estado = 'En Tránsito'
                        b.estados = ('Entregado','Atrasado','A Tiempo')
                        
                else:
                    #Atrasado
                    b.estado = 'Atrasado'
                    b.estados = ('A Tiempo','En Tránsito', 'Entregado')
        return render (request, 'modalLogistica.html', {'negocio':negocio,'lista_items':items,'clientes':cliente,'proveedores':proveedores})
    return render (request, 'modalLogistica.html')


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
                user = negocio.comprador.persona.user
                notif = Notificacion(
                    titulo=titulo,
                    descripcion = descri,
                    categoria=categoria,
                    hyperlink=reverse('negocio', args=[negocio.id,]),
                    user=user)
                notif.save()
            elif (ourid2[a] != ","):
                id_carga += str(ourid2[a])
            else:    
                negocio = Negocio.objects.get(id=int(id_carga))
                user = negocio.comprador.persona.user
                notif = Notificacion(
                    titulo=titulo,
                    descripcion = descri,
                    categoria=categoria,
                    hyperlink=reverse('negocio', args=[negocio.id,]),
                    user=user)
                notif.save()
                id_carga = ""
        data = {
            'result' : 'Alerta/s Enviada/s con éxito.',
            'estado': True
        }
        return JsonResponse(data)
    return JsonResponse(data)


def setLogistica(request):
    data = {
        'result' : 'Error, la operacion fracasó.'
    }
    if request.method == 'POST':
        ourid = request.POST['jsonText']
        lista_estados = []
        lista_ids = []
        comienzo = True
        id_carga = "" 
        ourid2 = ourid.replace('"', '')
        for a in ourid2:
            if (a == '[' or a == '-'):
                pass
            elif (a == ']'):
                lista_ids.append(int(id_carga))
            elif (comienzo):
                lista_estados.append(int(a))
                comienzo = False
            elif (a != ','):
                id_carga += str(a)
            else:
                comienzo = True
                lista_ids.append(int(id_carga))
                id_carga = ""
        today = date.today()
        negocioN = -1
        primero = True
        for a in range(len(lista_estados)):
            id_item = lista_ids[a]
            item = ItemPropuesta.objects.get(id=id_item)
            if (primero):
                negocioN = item.propuesta.negocio.id
                primero = False
            estado = lista_estados[a]            
            if (estado == 1 or estado == 4):
                item.fecha_real_entrega = None
                item.fecha_salida_entrega = None
            elif (estado == 2):
                item.fecha_real_entrega = None
                item.fecha_salida_entrega = today
            else:
                if (item.fecha_salida_entrega is None):
                    item.fecha_salida_entrega = today    
                item.fecha_real_entrega = today
            item.save()
        envio = request.POST['envio']
        negocio = Negocio.objects.get(id=negocioN)
        if (int(envio) == 1):
            receptor = request.POST['receptor']
            user = None
            if (int(receptor) == -1):
                user = negocio.comprador.persona.user
            else:
                logis = Logistica.objects.get(id=int(receptor))
                user = logis.persona.user
            titulo = request.POST['titulo']
            descri = request.POST['descri']
            notif = Notificacion(
                titulo=titulo,
                descripcion = descri,
                categoria="Logistica",
                hyperlink=reverse('negocio', args=[negocioN,]),
                user=user)
            notif.save()
            data = {
                'result' : 'Estados y Alerta enviados con éxito.'
            }
        else:
            notif = Notificacion(
                titulo="Estados de Articulos modificados",
                descripcion = "Estado/s modificado/s con éxito.",
                categoria="Logistica",
                hyperlink=reverse('negocio', args=[negocioN,]),
                user = negocio.comprador.persona.user)
            notif.save()
            data = {
                'result' : 'Estados cargados con éxito.'
            }
        return JsonResponse(data)
    return JsonResponse(data)


def sendAlertaLog(request):
    data = {
        'result' : 'Error, la operacion fracasó.'
    }
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descri = request.POST['descri']
        categoria = request.POST['categoria']
        idNegocio = request.POST['idNegocio']
        idN = int(idNegocio)
        negocio = Negocio.objects.get(id=idN)
        user = negocio.vendedor.persona.user
        notif = Notificacion(
            titulo=titulo,
            descripcion = descri,
            categoria=categoria,
            hyperlink=reverse('negocio', args=[negocio.id,]),
            user=user)
        notif.save()
        data = {
            'result' : 'Alerta Enviada con éxito.',
            'estado': True
        }
        return JsonResponse(data)
    return JsonResponse(data)

def reloadLog(request):
    grupo_activo = request.user.clase
    negociosCerrConf = None
    lnl = None
    if (grupo_activo == "Vendedor"):
        negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct())
        lnl = listaNL(request,negociosCerrConf)
    return render(request, 'tempAux/tableLogisR.html', {'lista_logistica':lnl})

def listaNCL(request, negocioFilter, tipo):
    lista_negocios = []
    persona = Persona.objects.get(user=request.user)
    empleadoL = None
    if (tipo=="L"):
        empleadoL = Logistica.objects.get(persona__id=persona.id)
    elif (tipo=="P"):
        empleadoL = Proveedor.objects.get(persona__id=persona.id)
    else:
        empleadoL = Administrador.objects.get(persona__id=persona.id)
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            if (tipo == "P"):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, proveedor__id=empleadoL.id)
            else:
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=empleadoL.empresa.id).values_list('articulo__ingrediente', flat=True)
            comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
            vendedor = negocio.vendedor.apellido +" "+negocio.vendedor.nombre
            if (items.count() > 0):
                lista = {
                    'fecha':fecha_p,
                    'items':list(items),
                    'comprador': comprador,
                    'vendedor': vendedor,
                    'empresa':negocio.comprador.empresa.razon_social,
                    'id_prop': id_prop
                }
                lista_negocios.append(lista)
    return lista_negocios

def listaNC(negocioFilter):
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
                'empresa':negocio.comprador.empresa.razon_social,
                'id_prop': id_prop
            }
            lista_negocios.append(lista)
    return lista_negocios

def semaforoVencimiento(negocioFilter):
    lista_vencidos = []
    lista_semanas = []
    lista_futuros = []
    today = date.today()
    today2 = datetime.today()
    """
    d1 = today.strftime("%d/%m/%Y")    
    diaA = int(d1[0:2])
    mesA = int(d1[3:5])
    añoA = int(d1[6:10])
    """
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True).values_list('articulo__ingrediente', 'fecha_pago')
            if (items.count() > 0):
                comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
                id_propuesta = id_prop        
                vencidos = False
                esta_semana = False
                futuros = False
                for a in items:                    
                    date_time_obj = datetime.strptime(a[1], "%d/%m/%Y")
                    if (date_time_obj < today2):
                        vencidos = True
                    else:
                        difDias = (today2 - date_time_obj).days                        
                        if ((difDias * (-1)) <= 7):
                            esta_semana = True
                        else:
                            futuros = True
                    """
                    diaP = int(a[1][0:2])
                    mesP = int(a[1][3:5])
                    añoP = int(a[1][6:10])
                    difD = (diaP - diaA)
                    difM = (mesP - mesA)
                    difA = (añoP - añoA)
                    proxMes = (diaP + 30 - diaA)
                    if ((mesA == 12 and mesP == 1) and (difA == 1)):
                        difM = 1
                    if ((difA < 0) or (difM < 0 and difA == 0) or ((((diaP > diaA) and (mesP < mesA)) or ((diaP < diaA) and (mesP == mesA))))):
                        vencidos = True 
                    elif ((diaP==diaA) and (mesP==mesA) and (añoP==añoA)):
                        esta_semana = True
                    elif (((mesP == mesA) and (difD < 8 and difD > 0)) or ((difM == 1) and ((proxMes < 8 and proxMes > 0) and (diaP < 7)))):
                        esta_semana = True
                    else:
                        futuros = True
                    """
                if (vencidos):
                    lista = {
                        'fecha':fecha_p,
                        'comprador': comprador,
                        'id_propuesta': id_propuesta,
                        'empresa':negocio.comprador.empresa.razon_social
                    }
                    lista_vencidos.append(lista)
                elif (esta_semana):
                    lista = {
                        'fecha':fecha_p,
                        'comprador': comprador,
                        'id_propuesta': id_propuesta,
                        'empresa':negocio.comprador.empresa.razon_social
                    }
                    lista_semanas.append(lista)
                else:
                    lista = {
                        'fecha':fecha_p,
                        'comprador': comprador,
                        'id_propuesta': id_propuesta,
                        'empresa':negocio.comprador.empresa.razon_social
                    }
                    lista_futuros.append(lista)
                vencidos = False
                esta_semana = False
                futuros = False
    return lista_vencidos,lista_semanas,lista_futuros

def reloadSem(request):
    grupo_activo = request.user.clase
    negociosCerrConf = None
    lnl = None
    if (grupo_activo == "Vendedor"):
        negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
        lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    return render(request, 'tempAux/tableSem.html', {'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos})

def createAlertaNV(request):
    data = {
        'result' : 'Error, la operacion fracasó.'
    }
    titulo = request.POST['titulo']
    descri = request.POST['descri']
    categoria = request.POST['categoria']
    res = 'Fecha/s de Pago cargada/s con éxito.'
    estado = True
    idNegocio = request.POST['idNegocio']
    idN = int(idNegocio)
    negocio = Negocio.objects.get(id=idN)
    user = None
    grupo_activo = request.user.clase
    text_categoria = "Presupuesto"
    if (categoria == "2"):
        text_categoria = "Logistica"
    elif (categoria == "1"):
        text_categoria = "Vencimiento"
    else:
        pass
    if (titulo != ""):
        notif = Notificacion(
            titulo=titulo,
            descripcion = descri,
            categoria=text_categoria,
            hyperlink=reverse('negocio', args=[negocio.id,]),
            user=negocio.vendedor.persona.user
        )
        notif.save()
        res = 'Alerta Enviada con éxito.'
        estado = True
    else:
        res = 'Error! El Titulo de la Alerta no puede estar en blanco.'
        estado = False
    data = {
        'result' : res,
        'estado' : estado
    }
    return JsonResponse(data)

def setFechaPagoReal(request):
    data = {
        'result' : 'Error, la operacion fracasó.'
    }
    if request.method == 'POST':
        ourid = request.POST['jsonText']
        vacio = request.POST['vacio']
        if (vacio == "0"):
            lista_ids = []
            id_carga = ""
            for a in ourid:
                if (a == '[' ):
                        pass
                elif (a == ']'):
                    lista_ids.append(int(id_carga))
                elif (a != ','):
                    id_carga += str(a)
                else:
                    lista_ids.append(int(id_carga))
                    id_carga = ""
            today = date.today()
            titulo = request.POST['titulo']
            descri = request.POST['descri']
            alerta = request.POST['tocadoAlerta'] 
            res = 'Fechas de Pago cargados con éxito.'
            estado = True
            idNegocio = request.POST['idNegocio']
            idN = int(idNegocio)
            negocio = Negocio.objects.get(id=idN)
            user = None
            user = negocio.comprador.persona.user
            grupo_activo = request.user.clase
            if (grupo_activo == "Vendedor"):
                user = negocio.comprador.persona.user
            else:
                user = negocio.vendedor.persona.user
            text_categoria = "Presupuesto"
            if (alerta=="0"):
                notif = Notificacion(
                    titulo="Pago de Artículos",
                    descripcion = "Se ha registrado el pago de uno/s articulo/s.",
                    categoria=text_categoria,
                    hyperlink=reverse('negocio', args=[negocio.id,]),
                    user=user
                )
                notif.save()
                res = 'Fechas de Pago cargadas con éxito'
                estado = True
            else:
                notif = Notificacion(
                    titulo=titulo,
                    descripcion = descri,
                    categoria=text_categoria,
                    hyperlink=reverse('negocio', args=[negocio.id,]),
                    user=user
                )
                notif.save()
                res = 'Fechas de Pago cargadas con éxito y notificación enviada con éxito.'
                estado = True
            for b in lista_ids:
                item = ItemPropuesta.objects.get(id=b)
                item.fecha_real_pago = today
                item.save()
        else:
            res = 'Error! No se ha seleccionado ningún item.'
            estado = False
        data = {
            'result' : res,
            'estado' : estado
        }
        return JsonResponse(data)
    return JsonResponse(data)

def detalleSemaforo(request):
    if request.method == 'POST':
        idProp = request.POST['idProp']
        ind = request.POST['ind']
        propuesta = Propuesta.objects.get(id = idProp)
        negocio = Negocio.objects.get(id=propuesta.negocio.id)
        grupo_activo = request.user.clase
        items = None
        if (grupo_activo == 'Administrador'):
            administradorL = request.User
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, fecha_real_pago__isnull=True, empresa__id=administradorL.empresa.id)        
        elif (grupo_activo == 'Proveedor'):
            proveedorP = request.user
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, fecha_real_pago__isnull=True, proveedor__id=proveedorP.id)        
        else:
            items = ItemPropuesta.objects.filter(propuesta__id = idProp, fecha_real_pago__isnull=True)
        today = datetime.today()
        for a in items:
            if (ind == "1"):
                fechaPago = datetime.strptime(a.fecha_pago, "%d/%m/%Y")
                resultado = calcularVencAtr(fechaPago, today)
                if (resultado):
                    a.estado = "A Tiempo"
                else:
                    a.estado = "Vencido"
            else:
                a.estado = "A Tiempo"
        return render (request, 'modalSemaforo.html', {'negocio':negocio, 'propuesta':propuesta,'items':items})
    return redirect(render)

def calcularVencAtr(a, b):
    if (a < b):
        return True
    return False    
def listaItemsPorVencer(listaNegociosC):
    lista_Items = []
    for a in listaNegociosC:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            items = list(ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente','fecha_pago'))
            for b in items:
                lista_Items.append(b)
    return lista_Items



def listasNA(negocioFilter, tipo):
    lista_negocios = []
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp','envio_comprador','visto')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            envio = propuesta[0][2]
            visto = propuesta[0][3]
            valor_visto = "No"
            if (visto):
                valor_visto = "Si"
            if (envio == tipo):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
                comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
                lista = {
                    'fecha':fecha_p,
                    'items':list(items),
                    'comprador': comprador,
                    'empresa':(negocio.comprador.empresa.razon_social),
                    'visto': valor_visto,
                    'id_prop': id_prop
                }
                lista_negocios.append(lista)
            else:
                pass
    return lista_negocios

def listasNAA(request,negocioFilter, tipo):
    lista_negocios = []
    persona = Persona.objects.get(user=request.user)
    empleadoL = Administrador.objects.get(persona__id=persona.id)
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp','envio_comprador','visto')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            envio = propuesta[0][2]
            visto = propuesta[0][3]
            valor_visto = "No"
            if (visto):
                valor_visto = "Si"
            if (envio == tipo):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=empleadoL.empresa.id).values_list('articulo__ingrediente', flat=True)
                if (items.count() > 0):
                    comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
                    lista = {
                        'fecha':fecha_p,
                        'items':list(items),
                        'comprador': comprador,
                        'empresa':(negocio.comprador.empresa.razon_social),
                        'visto': valor_visto,
                        'id_prop': id_prop
                    }
                    lista_negocios.append(lista)
            else:
                pass
    return lista_negocios

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
    sheet_writer()
    return HttpResponseRedirect(reverse('carga_excel'))

def crear_negocio(request, comprador, vendedor, isComprador, observacion):
    created_by = None
    if isComprador:
        vendedor_obj = MyUser.objects.get(email=vendedor)
        comprador_obj = request.user
        created_by = request.user.get_full_name()
        negocio = Negocio(
            comprador = comprador_obj,
            vendedor = vendedor_obj
            )
        negocio.save()
    else:
        comprador_obj = MyUser.objects.get(email=comprador)
        vendedor_obj = request.user
        created_by = request.user.get_full_name()
        negocio = Negocio(
            comprador = comprador_obj,
            vendedor = vendedor_obj
            )
        negocio.save()

    subject = "Se creó un nuevo negocio"
    texto = f"""
    El nuevo negocio tiene identificador BVi-{negocio.id} y fue creado por {created_by}.
    Hacé click en el botón de abajo para ver el nuevo negocio.
    """
    protocol = "http://"
    domain = Site.objects.get_current().domain
    full_negociacion_url =  protocol + domain + reverse('negocio', args=[negocio.id,])
    recipient_list = [negocio.vendedor.email, negocio.comprador.email]
    context = {'titulo' : subject, 'color' : "", 'texto' : texto, 'obs' : observacion, 'url' : full_negociacion_url}

    email_response = email_send(subject, recipient_list, 'email/negocio.txt', 'email/negocio.html', context)

    return negocio
    

def crear_propuesta(negocio,observacion,isComprador):
    propuesta = Propuesta(
        negocio=negocio,
        observaciones=observacion,
        timestamp=datetime.now(),
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
                'usuario': vend.get_full_name()
            }
            vendedores.append(tmp)
        return JsonResponse(list(vendedores), safe=False)


class APIDistribuidor(View):
    def get(self,request):
        proveedores = []
        for pro in MyUser.objects.filter(clase='Proveedor'):
            tmp = {
                'nombre':pro.get_full_name()
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

def filterArticulo(request, ingrediente):
    empresas = Articulo.objects.filter(ingrediente=ingrediente).values("empresa__nombre_comercial")
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



class ListProveedorView(View):
    def get(self, request, *args, **kwargs):
        all_proveedores = Proveedor.objects.all()
        return render(request, 'consultar_proveedor.html', {'proveedores':all_proveedores})    


class ProveedorView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": ProveedorForm()}
        if ("pk" in kwargs):
            context["proveedor"] = Proveedor.objects.get(pk=kwargs["pk"])
            context["form"] = ProveedorForm(instance=context["proveedor"])
        return render(request, 'proveedor.html', context)

    def post(self, request, *args, **kwargs):
        proveedor = None
        if ("pk" in kwargs):
            proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            return redirect('admin')
        return render(request, 'proveedor.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        proveedor.delete()
        return HttpResponse(code=200)

class ListCompradorView(View):
    def get(self, request, *args, **kwargs):
        all_compradores = MyUser.objects.filter(clase='Comprador')
        return render(request, 'consultar_comprador.html', {'compradores':all_compradores})    


class CompradorView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": CompradorForm()}
        if ("pk" in kwargs):
            context["comprador"] = Comprador.objects.get(pk=kwargs["pk"])
            context["form"] = CompradorForm(instance=context["comprador"])
        return render(request, 'comprador.html', context)

    def post(self, request, *args, **kwargs):
        comprador = None
        if ("pk" in kwargs):
            comprador = Comprador.objects.get(pk=kwargs["pk"])
        form = CompradorForm(request.POST, instance=comprador)
        if form.is_valid():
            comprador = form.save()
            return redirect("admin")
        return render(request, 'comprador.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        comprador = Comprador.objects.get(pk=kwargs["pk"])
        comprador.delete()
        return HttpResponse(status=200)

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

class PropuestaView(View):

    def get(self, request, *args, **kwargs):
        context = {
        "form": PropuestaForm(),
        "compradores": Comprador.objects.all(),
        "proveedores": Proveedor.objects.all(),
        "articulos": Articulo.objects.all()}
        if ("pk" in kwargs):
            context["propuesta"] = Propuesta.objects.get(pk=kwargs["pk"])
            context["form"] = PropuestaForm(instance=context["propuesta"])
        return render(request, 'propuestas.html', context)

    def post(self, request, *args, **kwargs):
        propuesta = None
        if ("pk" in kwargs):
            propuesta = Propuesta.objects.get(pk=kwargs["pk"])
        form = PropuestaForm(request.POST, instance=propuesta)
        if form.is_valid():
            propuesta = form.save()
            return redirect('propuesta', pk=propuesta.pk)
        return render(request, 'propuesta.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        propuesta = Propuesta.objects.get(pk=kwargs["pk"])
        propuesta.delete()
        return HttpResponse(code=200)

class NegocioView(View):
    def get(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, pk=kwargs["pk"])

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
            last['items'].append(art)
        context = {
            "negocio": negocio,
            "propuestas": reversed(negocio.propuestas.all().reverse()),
            "last": json.dumps(last,cls=DjangoJSONEncoder),
            "divisas": DIVISA_CHOICES,
            'tasas': TASA_CHOICES,
            "distribuidores": MyUser.objects.filter(clase='Proveedor'),
            "tipo_pagos": TipoPago.objects.all(),
            "arts": Articulo.objects.all()
        }
        return render(request, 'negocio.html', context)

    def post(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, pk=kwargs["pk"])
        data = json.loads(request.body)
        completed = True
        observaciones = "No hay observaciones" if not data["observaciones"] else data["observaciones"]
        res = None
        with transaction.atomic():
            prop = Propuesta(
                negocio=negocio,
                observaciones=data["observaciones"],
                envio_comprador=request.user.clase == 'Comprador'
            )
            prop.save()
            for item in data["items"]:
                tmp = ItemPropuesta()
                for f in tmp._meta.get_fields():
                    key = f.name
                    if key=="propuesta" or key=="id":
                        continue
                    value = item[key]
                    if key == "proveedor" and value == None:
                        setattr(tmp, key, None)
                    if f.is_relation:
                        if not (key == "proveedor" and value == None):
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
        if (prop.envio_comprador):
            user=negocio.comprador
        else:
            user=negocio.vendedor
        notif = Notificacion(
            titulo=titulo,
            categoria=categoria,
            hyperlink=reverse('negocio', args=[negocio.id,]),
            user=user
        )
        notif.save()

        propuesta = Propuesta.objects.filter(negocio=negocio).last()
        itemsProp = ItemPropuesta.objects.all().filter(propuesta=propuesta.id)
        acc = []
        
        for i in itemsProp:
            acc.append(i.aceptado)
        
        if all(acc) and not itemsProp.count() == 0:
            if not negocio.aprobado:
                negocio.aprobado = True
                negocio.fecha_cierre = datetime.now()
                negocio.save()

        if len(data.get('items')) == 0:
            negocio.cancelado = True
            negocio.fecha_cierre = datetime.now()
            negocio.save()

        # send email

        formatted_fecha_cierre = ""
        color = ""
        texto = ""
        negocio_update = False

        fecha_cierre = negocio.fecha_cierre
        if fecha_cierre is not None:
            fecha = formats.date_format(fecha_cierre, "SHORT_DATE_FORMAT")
            hora = formats.time_format(fecha_cierre, "TIME_FORMAT")
            formatted_fecha_cierre = f"{fecha} a las {hora} hs"

        pre_titulo = f"Presupuesto de {request.user.get_full_name()}"
        pre_text = f"El presupuesto del negocio {negocio.get_id_de_neg()} ha sido"
        pos_text = "Hacé click en el botón de abajo para ver el estado de la negociación."
        pos_cierre_text = f"El negocio cerró el día {formatted_fecha_cierre}."

        if negocio.aprobado:
            titulo = f"{pre_titulo} aprobado"
            color = "green"
            texto = f"""
            {pre_text} aprobado. {pos_cierre_text}

            {pos_text}
            """
        elif negocio.cancelado:
            titulo = f"{pre_titulo} cancelado"
            color = "red"
            texto = f"""
            {pre_text} cancelado. {pos_cierre_text}

            {pos_text}
            """
        else:
            negocio_update = True

        full_negociacion_url = request.build_absolute_uri(reverse('negocio', args=[negocio.id,]))
        recipient_list = [negocio.vendedor.email, negocio.comprador.email]
        context = {'titulo' : titulo, 'color' : color, 'texto' : texto, 'obs' : observaciones, 'url' : full_negociacion_url}

        if not negocio_update:
            email_response = email_send(categoria, recipient_list, 'email/negocio.txt', 'email/negocio.html', context)
            print(email_response)
        
        res = render(request, 'negocio.html')
        
        #NOTE: acá tengo pensado mostrar un mensaje en el template que me diga si el envío del mail dió error
        # if email_response == 1:
        #     res = render(request, 'negocio.html')
        # else:
        #     res = render(request, 'negocio.html', {'email_error' : True, 'email_error_response' : email_response})

        return res

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

class APIArticulos(View):
    def get(self,request):
        articulos = None
        if (request.GET.get('search', None)):
            words = request.GET['search'].split(" ")
            query = reduce(operator.and_, (Q(ingrediente__icontains=word) | Q(empresa__nombre_comercial__icontains=word) for word in words))
            articulos = Articulo.objects.filter(query)
        else:
            articulos = Articulo.objects.all()
        return JsonResponse(list(articulos.values("empresa__nombre_comercial", "ingrediente", "id", "marca")), safe=False)

    def post(self,request):
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
            empresa = actual.get("Empresa")
            ingrediente = actual.get("Ingrediente")
            distribuidor = actual.get("Distribuidor")
            domicilio = actual.get("Destino")
            tipo_pago_str = actual.get("Tipo de pago")
            divisa_tmp = actual.get("Divisa")
            divisa = get_from_tuple(DIVISA_CHOICES,divisa_tmp)
            tasa_tmp = actual.get("Tasa")
            tasa = get_from_tuple(TASA_CHOICES,tasa_tmp)
            # NOTE: Articulo filtra por nombre comercial (muchos articulos con el mismo nombre de empresa),
            # por lo que la query arroja resultados que pueden ser no deseados.
            articulo = Articulo.objects.filter(empresa__nombre_comercial=empresa, ingrediente=ingrediente).first()
            # try:
            #     domicilio = Domicilio.objects.get(direccion=domicilio_str)
            # except ObjectDoesNotExist:
            #     domicilio = Domicilio(direccion=domicilio_str)
            #     domicilio.save()

            #quilombo para traer al objecto empresa
            if isComprador:
                proveedor = None
            elif len(distribuidor.strip()) != 0:
                get_distribuidor = actual.get("Distribuidor").split(" ")
                nombre = get_distribuidor[0].strip()
                apellido = get_distribuidor[1].strip()
                #distribuidor_usr = User.objects.filter(nombre=get_distribuidor[0],apellido=get_distribuidor[1]).values("id")
                #distribuidor_per = Persona.objects.filter(user_id__in=distribuidor_usr)
                proveedor = MyUser.objects.get(nombre=nombre,apellido=apellido)
                # prov_per = Persona.objects.filter(user_id__in=prov_usr)
                # proveedor = Proveedor.objects.get(persona_id__in=prov_per)
                #distribuidor = Empresa.objects.get(id__in=distribuidor_emp)
            else:
                proveedor = None

            #traer el objecto tipo de pago
            if len(actual.get("Tipo de pago").strip()) != 0:
                tipo_pago = TipoPago.objects.get(nombre=tipo_pago_str)
            else:
                tipo_pago = None

            if len(actual.get("Precio venta").strip()) != 0:
                precio_venta = actual.get("Precio venta")
            else:
                precio_venta = 0.0

            if isComprador:
                precio_compra = 0.0
            elif len(actual.get("Precio compra").strip()) != 0:
                precio_compra = actual.get("Precio compra")
            else:
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
        return JsonResponse(negocio.pk, safe=False)

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