import json
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.core import serializers
from django.db import transaction
from django.urls import reverse
from django.utils.dateparse import parse_date

from .forms import *
from .models import *
from .choices import DIVISA_CHOICES, TASA_CHOICES
from .scriptModels import *
from datetime import date
from BAapp.utils.utils import *

def landing_page(request):
	return render(request, 'Principal.html')
def cuentas(request):
    return render(request, 'cuentas.html')

def admin(request):
    return render(request,'admin.html')

def chat(request):
    return render(request,'chat.html')

def inicio(request):
    #loadModels(request)
    return render(request,'inicio.html')

def todos_negocios(request):
    return render(request, 'todos_negocios.html')

def testeo(request):
    return render(request, 'testeo.html')

def cliente(request):
    return render(request, 'cliente.html')

def vendedor(request):
    #Negocios en Procesos
    negociosAbiertos = list(Negocio.objects.filter(fecha_cierre__isnull=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnr = listasNA(negociosAbiertos, True)
    lnp = listasNA(negociosAbiertos, False)
    #lnc = Lista Negocios Confirmados
    negociosCerrConf = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=True).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnc = listaNC(negociosCerrConf)
    lista_vencidos,lista_semanas,lista_futuros = semaforoVencimiento(negociosCerrConf)
    #lnnc = Linta de Negocios Rechazados
    negociosCerrRech = list(Negocio.objects.filter(fecha_cierre__isnull=False, aprobado=False).values_list('id', flat=True).order_by('-timestamp').distinct()[:3])
    lnnc = listaNC(negociosCerrRech)
    return render(request, 'vendedor.html', {'vencimiento_futuro':lista_futuros,'vencimiento_semanal':lista_semanas,'vencidos':lista_vencidos,'presupuestos_recibidos':list(lnr),'presupuestos_negociando':list(lnp),'negocios_cerrados_confirmados':list(lnc),'negocios_cerrados_no_confirmados':list(lnnc)})
    
def listaNC(negocioFilter):
    lista_negocios = []
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        id_prop = propuesta[0][0]
        fecha_p = propuesta[0][1]
        items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
        comprador = negocio.comprador.persona.user.last_name +" "+negocio.comprador.persona.user.first_name
        lista = {
            'fecha':fecha_p,
            'items':list(items),
            'comprador': comprador,
            'empresa':negocio.comprador.empresa.razon_social
        }
        lista_negocios.append(lista)
    return lista_negocios

def semaforoVencimiento(negocioFilter):
    lista_vencidos = []
    lista_semanas = []
    lista_futuros = []
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    diaA = int(d1[0:2])
    mesA = int(d1[3:5])
    añoA = int(d1[6:10])
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        id_prop = propuesta[0][0]
        fecha_p = propuesta[0][1]
        items = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True).values_list('articulo__ingrediente', 'fecha_pago')
        if (items.count() > 0):
            comprador = negocio.comprador.persona.user.last_name +" "+negocio.comprador.persona.user.first_name
            id_propuesta = id_prop        
            vencidos = False
            esta_semana = False
            futuros = False
            for a in items:
                diaP = int(a[1][0:2])
                mesP = int(a[1][3:5])
                añoP = int(a[1][6:10])
                difD = (diaP - diaA)
                difM = (mesP - mesA)
                difA = (añoP - añoA)
                proxMes = (diaP + 30 - diaA)
                if ((mesA == 12 and mesP == 1) and (difA == 1)):
                    difM = 1
                if ((difA < 0) or ((((diaP > diaA) and (mesP < mesA)) or ((diaP < diaA) and (mesP == mesA))))):
                    vencidos = True
                elif ((diaP==diaA) and (mesP==mesA) and (añoP==añoA)):
                    esta_semana = True
                elif (((mesP == mesA) and (difD < 8 and difD > 0)) or ((difM == 1) and ((proxMes < 8 and proxMes > 0) and (diaP < 7)))):
                    esta_semana = True
                else:
                    futuros = True
                
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

def setFechaPagoReal(request):
    data = {
        'result' : 'Error, la operacion fracaso.'
    }
    if request.method == 'POST':
        ourid = request.POST['jsonText']
        lista_ids = []
        for a in ourid:
            if (a == "[" or a == "]" or a == ","):
                pass
            else:
                lista_ids.append(int(a))
        today = date.today()
        for b in lista_ids:
            item = ItemPropuesta.objects.get(id=b)
            item.fecha_real_pago = today
            item.save()
        data = {
            'result' : 'Fechas de Pago cargados con exito.'
        }
        return JsonResponse(data)
    return JsonResponse(data)

def detalleSemaforo(request):
    if request.method == 'POST':
        idProp = request.POST['idProp']
        propuesta = Propuesta.objects.get(id = idProp)
        negocio = Negocio.objects.get(id=propuesta.negocio.id)
        items = ItemPropuesta.objects.filter(propuesta__id = idProp, fecha_real_pago__isnull=True).order_by('fecha_pago')
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        diaA = int(d1[0:2])
        mesA = int(d1[3:5])
        añoA = int(d1[6:10])
        for a in items:
            diaP = int(a.fecha_pago[0:2])
            mesP = int(a.fecha_pago[3:5])
            añoP = int(a.fecha_pago[6:10])
            difD = (diaP - diaA)
            difM = (mesP - mesA)
            difA = (añoP - añoA)
            proxMes = (diaP + 30 - diaA)
            if ((mesA == 12 and mesP == 1) and (difA == 1)):
                difM = 1
            if ((difA < 0) or ((((diaP > diaA) and (mesP < mesA)) or ((diaP < diaA) and (mesP == mesA))))):
                a.estado = "Vencido"
            elif ((diaP==diaA) and (mesP==mesA) and (añoP==añoA)):
                a.estado = "En Tiempo"
            elif (((mesP == mesA) and (difD < 8 and difD > 0)) or ((difM == 1) and ((proxMes < 8 and proxMes > 0) and (diaP < 7)))):
                a.estado = "En Tiempo"
            else:
                a.estado = "En Tiempo"       

        return render (request, 'modalSemaforo.html', {'negocio':negocio, 'propuesta':propuesta,'items':items})
    return redirect(render)

def listaItemsPorVencer(listaNegociosC):
    lista_Items = []
    for a in listaNegociosC:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
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
        id_prop = propuesta[0][0]
        fecha_p = propuesta[0][1]
        envio = propuesta[0][2]
        visto = propuesta[0][3]
        valor_visto = "No"
        if (visto):
            valor_visto = "Si"
        if (envio == tipo):
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
            comprador = negocio.comprador.persona.user.last_name +" "+negocio.comprador.persona.user.first_name
            lista = {
                'fecha':fecha_p,
                'items':list(items),
                'comprador': comprador,
                'empresa':(negocio.comprador.empresa.razon_social),
                'visto': valor_visto
            }
            lista_negocios.append(lista)
        else:
            pass
    return lista_negocios
    

class carga_excel(View):
    
    def get(self,request):    
        return render(request, 'carga_excel.html')
    
    def post(self,request):
        sheet_reader(request.FILES["myfile"])
        return self.get(request)

def crear_negocio(comprador, vendedor):
    chunks = comprador.split(' ')
    comprador_usr = User.objects.filter(first_name=chunks[0], last_name=chunks[1]).values("id")
    comprador_per = Persona.objects.filter(user_id__in=comprador_usr)
    comprador_obj = Comprador.objects.get(persona_id__in=comprador_per)

    # vendedor_per = Persona.objects.filter(user=vendedor).values("id")
    # vendedor_obj = Vendedor.objects.get(persona_id__in=1)
    negocio = Negocio(
        comprador = comprador_obj,
        vendedor = None,
        fecha_cierre = datetime.datetime.now(),
        fecha_entrega = datetime.datetime.now(),
        tipo_pago = "tipo de pago",
        )
    negocio.save()
    return negocio 

def crear_propuesta(negocio):
    propuesta = Propuesta(
        negocio=negocio,
        observaciones="",
        timestamp=datetime.datetime.now(),
        envio_comprador=False,
        visto=False,
        )    
    propuesta.save()
    return propuesta

class APIArticulos(View):
    def get(self,request):
        articulos = None
        if (request.GET.get('search', None)):
            words = request.GET['search'].split(" ")
            for i in range(len(words)):
                words[i] = "+{}*".format(words[i])
            searchStr = " ".join(words)
            articulos = Articulo.objects.search(searchStr)
        else:
            articulos = Articulo.objects.all()
        return JsonResponse(list(articulos.values("marca", "ingrediente","id")), safe=False)

    def post(self,request):
        recieved = json.loads(request.body.decode("utf-8"))
        comprador = recieved.get("comprador")
        vendedor = recieved.get("vendedor")
        negocio = crear_negocio(comprador, vendedor)
        propuesta = crear_propuesta(negocio)
        data = recieved.get("data")
        domicilio = Domicilio.objects.get(id=1)
        for i in range(len(data)):
            actual = data[i]
            marca = actual.get("Marca")
            ingrediente = actual.get("Ingrediente")
            fecha_pago = actual.get("Fecha de pago")
            articulo = Articulo.objects.get(marca=marca, ingrediente=ingrediente)

            #quilombo para traer al objecto proveedor
            get_distribuidor = actual.get("Distribuidor").split(" ")
            distribuidor_usr = User.objects.filter(first_name=get_distribuidor[0],last_name=get_distribuidor[1]).values("id")
            distribuidor_per = Persona.objects.filter(user_id__in=distribuidor_usr)
            distribuidor_emp = Proveedor.objects.filter(persona_id__in=distribuidor_per).values("empresa_id")
            distribuidor = Empresa.objects.get(id__in=distribuidor_emp)

            item = ItemPropuesta(
                articulo=articulo, 
                distribuidor=distribuidor,
                propuesta=propuesta,
                cantidad=actual.get("Cantidad"),
                precio=actual.get("Precio X unidad"),
                divisa="",
                destino=domicilio,
                aceptado=False,
                fecha_pago=fecha_pago)
            item.save()
        return redirect('negocio', pk=str(negocio.pk))
        #return HttpResponse(status=200)

class APIComprador(View):
    def get(self,request):
        compradores = []
        for comp in Comprador.objects.all().values("persona_id","empresa_id"):
            try:
                tmp_persona = Persona.objects.filter(id=comp['persona_id']).values("user")[0]['user']
            except Exception:
                context = Persona.objects.none()
            tmp = {
                'usuario':User.objects.get(id=tmp_persona).get_full_name(),
                'empresa':Empresa.objects.filter(id=comp['empresa_id']).values("razon_social")[0]['razon_social'],
            }
            compradores.append(tmp)
        return JsonResponse(list(compradores), safe=False)


class APIDistribuidor(View):
    def get(self,request):
        distribuidores = []
        for pro in Proveedor.objects.all().values("persona_id","empresa_id"):
            try:
                tmp_persona = Persona.objects.filter(id=pro['persona_id']).values("user")[0]['user']
            except Exception:
                context = Persona.objects.none()
            tmp = {
                'nombre':User.objects.get(id=tmp_persona).get_full_name(),
                'empresa':Empresa.objects.filter(id=pro['empresa_id']).values("razon_social")[0]['razon_social'],
            }
            distribuidores.append(tmp)
        return JsonResponse(list(distribuidores), safe=False)

def filterArticulo(request, ingrediente):
    marcas = Articulo.objects.filter(ingrediente=ingrediente).values("marca")
    return JsonResponse(list(marcas), safe=False)

        

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
            return redirect('proveedor', pk=proveedor.pk)
        return render(request, 'proveedor.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        proveedor.delete()
        return HttpResponse(code=200)



class ListCompradorView(View):
    def get(self, request, *args, **kwargs):
        all_compradores = Comprador.objects.all()
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
            return redirect("comprador", pk=comprador.pk)
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
        data = negocio.propuestas.last()
        last = {
            'items': [],
            'observaciones': data.observaciones
        }
        comp = request.user.groups.filter(name="comprador").exists()
        if (comp==data.envio_comprador):
            data.visto = True
            data.save()
        for i in data.items.all():
            art = {}
            for f in i._meta.get_fields():
                val = getattr(i,f.name)
                if (f.is_relation):
                    art[f.name] = val.id
                else:
                    art[f.name] = val
            last['items'].append(art)
        context = {
            "negocio": negocio,
            "propuestas": reversed(negocio.propuestas.all().reverse()[:2]),
            "last": json.dumps(last),
            "divisas": DIVISA_CHOICES,
            "distribuidores": Empresa.objects.all()
        }
        return render(request, 'negocio.html', context)

    def post(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, pk=kwargs["pk"])
        data = json.loads(request.body)
        completed = True
        with transaction.atomic():
            prop = Propuesta(
                negocio=negocio,
                observaciones=data["observaciones"],
                envio_comprador=request.user.groups.filter(name="comprador").exists()
            )
            prop.save()
            for item in data["items"]:
                tmp = ItemPropuesta()
                for f in tmp._meta.get_fields():
                    if (f.name=="propuesta" or f.name=="id"):
                        continue
                    print(f.name)
                    if (f.is_relation):
                        obj = get_object_or_404(
                            f.related_model,
                            pk=item[f.name]
                        )
                        setattr(tmp, f.name, obj)
                    else:
                        setattr(
                            tmp, 
                            f.name, 
                            item[f.name]
                        )
                tmp.propuesta = prop
                tmp.save()
                completed &= tmp.aceptado

        titulo = "Propuesta de {} {}".format(
            request.user.get_full_name(),
            "aceptada" if completed else "actualizada"
        )
        catergoria = "Propuesta {}".format(
            "aceptada" if completed else "actualizada"
        )
        user = None
        if (prop.envio_comprador):
            user=negocio.comprador.persona.user
        else:
            user=negocio.vendedor.persona.user
        notif = models.Notificacion(
            titulo=titulo,
            categoria=categoria,
            hyperlink=reverse('negocio', args=[negocio.id,]),
            user=user
        )
        notif.save()
        return render(request, 'negocio.html')


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
        id_prop = propuesta[0][0]
        fecha_p = propuesta[0][1]
        envio = propuesta[0][2]
        if (envio == tipo):
            items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
            comprador = negocio.comprador.persona.user.last_name +" "+negocio.comprador.persona.user.first_name
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
        id_prop = propuesta[0][0]
        fecha_p = propuesta[0][1]
        items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
        comprador = negocio.comprador.persona.user.last_name +" "+negocio.comprador.persona.user.first_name
        lista = {
            'fecha':fecha_p,
            'items':list(items),
            'comprador': comprador,
            'empresa':negocio.comprador.empresa.razon_social
        }
        lista_negocios.append(lista)
    return lista_negocios



def crear_negocio(comprador, vendedor):
    chunks = comprador.split(' ')
    comprador_usr = User.objects.filter(first_name=chunks[0], last_name=chunks[1]).values("id")
    comprador_per = Persona.objects.filter(user_id__in=comprador_usr)
    comprador_obj = Comprador.objects.get(persona_id__in=comprador_per)

    # vendedor_per = Persona.objects.filter(user=vendedor).values("id")
    # vendedor_obj = Vendedor.objects.get(persona_id__in=1)
    negocio = Negocio(
        comprador = comprador_obj,
        vendedor = None,
        fecha_cierre = datetime.datetime.now(),
        )
    negocio.save()
    return negocio 

def crear_propuesta(negocio):
    propuesta = Propuesta(
        negocio=negocio,
        observaciones="",
        timestamp=datetime.datetime.now(),
        envio_comprador=False,
        visto=False,
        )    
    propuesta.save()
    return propuesta

class APIArticulos(View):
    def get(self,request):
        articulos = None
        if (request.GET.get('search', None)):
            words = request.GET['search'].split(" ")
            for i in range(len(words)):
                words[i] = "+{}*".format(words[i])
            searchStr = " ".join(words)
            articulos = Articulo.objects.search(searchStr)
        else:
            articulos = Articulo.objects.all()
        return JsonResponse(list(articulos.values("marca", "ingrediente","id")), safe=False)

    def post(self,request):
        recieved = json.loads(request.body.decode("utf-8"))
        comprador = recieved.get("comprador")
        vendedor = recieved.get("vendedor")
        negocio = crear_negocio(comprador, vendedor)
        propuesta = crear_propuesta(negocio)
        data = recieved.get("data")
        domicilio = Domicilio.objects.get(id=1)
        for i in range(len(data)):
            actual = data[i]
            marca = actual.get("Marca")
            ingrediente = actual.get("Ingrediente") 
            tipo_pago_str = actual.get("Tipo de pago")
            divisa_tmp = actual.get("Divisa")
            divisa = get_from_tuple(DIVISA_CHOICES,divisa_tmp)
            tasa_tmp = actual.get("Tasa")
            tasa = get_from_tuple(TASA_CHOICES,tasa_tmp)
            articulo = Articulo.objects.get(marca=marca, ingrediente=ingrediente)

            #quilombo para traer al objecto proveedor
            get_distribuidor = actual.get("Distribuidor").split(" ")
            distribuidor_usr = User.objects.filter(first_name=get_distribuidor[0],last_name=get_distribuidor[1]).values("id")
            distribuidor_per = Persona.objects.filter(user_id__in=distribuidor_usr)
            distribuidor_emp = Proveedor.objects.filter(persona_id__in=distribuidor_per).values("empresa_id")
            distribuidor = Empresa.objects.get(id__in=distribuidor_emp)

            #traer el objecto tipo de pago
            tipo_pago = TipoPago.objects.get(nombre=tipo_pago_str)
            item = ItemPropuesta(
                articulo=articulo, 
                distribuidor=distribuidor,
                propuesta=propuesta,
                precio_venta=actual.get("Precio venta"),
                precio_compra=actual.get("Precio compra"),
                cantidad=actual.get("Cantidad"),
                divisa=divisa,
                tipo_pago=tipo_pago,
                tasa=tasa,
                destino=domicilio,
                aceptado=False,
                fecha_pago=actual.get("Fecha de pago"),
                fecha_entrega=actual.get("Fecha de entrega"),)
            item.save()
        #return JsonResponse(negocio.pk, safe=False)
        return HttpResponse(status=200)

class APIComprador(View):
    def get(self,request):
        compradores = []
        for comp in Comprador.objects.all().values("persona_id","empresa_id"):
            try:
                tmp_persona = Persona.objects.filter(id=comp['persona_id']).values("user")[0]['user']
            except Exception:
                context = Persona.objects.none()
            tmp = {
                'usuario':User.objects.get(id=tmp_persona).get_full_name(),
                'empresa':Empresa.objects.filter(id=comp['empresa_id']).values("razon_social")[0]['razon_social'],
            }
            compradores.append(tmp)
        return JsonResponse(list(compradores), safe=False)


class APIDistribuidor(View):
    def get(self,request):
        distribuidores = []
        for pro in Proveedor.objects.all().values("persona_id","empresa_id"):
            try:
                tmp_persona = Persona.objects.filter(id=pro['persona_id']).values("user")[0]['user']
            except Exception:
                context = Persona.objects.none()
            tmp = {
                'nombre':User.objects.get(id=tmp_persona).get_full_name(),
                'empresa':Empresa.objects.filter(id=pro['empresa_id']).values("razon_social")[0]['razon_social'],
            }
            distribuidores.append(tmp)
        return JsonResponse(list(distribuidores), safe=False)

def filterArticulo(request, ingrediente):
    marcas = Articulo.objects.filter(ingrediente=ingrediente).values("marca")
    return JsonResponse(list(marcas), safe=False)

def getPagos(request):
    tipo_pago = TipoPago.objects.all().values("nombre")
    return JsonResponse(list(tipo_pago), safe=False)
        

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
            return redirect('proveedor', pk=proveedor.pk)
        return render(request, 'proveedor.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        proveedor.delete()
        return HttpResponse(code=200)



class ListCompradorView(View):
    def get(self, request, *args, **kwargs):
        all_compradores = Comprador.objects.all()
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
            return redirect("comprador", pk=comprador.pk)
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
        data = negocio.propuestas.last()
        last = {
            'items': [],
            'observaciones': data.observaciones
        }
        comp = request.user.groups.filter(name="comprador").exists()
        if (comp==data.envio_comprador):
            data.visto = True
            data.save()
        for i in data.items.all():
            art = {}
            for f in i._meta.get_fields():
                val = getattr(i,f.name)
                if (f.is_relation):
                    art[f.name] = val.id
                else:
                    art[f.name] = val
            last['items'].append(art)
        context = {
            "negocio": negocio,
            "propuestas": reversed(negocio.propuestas.all().reverse()[:2]),
            "last": json.dumps(last),
            "divisas": DIVISA_CHOICES,
            "distribuidores": Empresa.objects.all()
        }
        return render(request, 'negocio.html', context)

    def post(self, request, *args, **kwargs):
        negocio = get_object_or_404(Negocio, pk=kwargs["pk"])
        data = json.loads(request.body)
        completed = True
        with transaction.atomic():
            prop = Propuesta(
                negocio=negocio,
                observaciones=data["observaciones"],
                envio_comprador=request.user.groups.filter(name="comprador").exists()
            )
            prop.save()
            for item in data["items"]:
                tmp = ItemPropuesta()
                for f in tmp._meta.get_fields():
                    if (f.name=="propuesta" or f.name=='id'):
                        continue
                    if (f.is_relation):
                        obj = get_object_or_404(
                            f.related_model,
                            pk=item[f.name]
                        )
                        setattr(tmp,f.name,obj)
                    else:
                        setattr(
                            tmp, 
                            f.name, 
                            item[f.name]
                        )
                tmp.propuesta = prop
                tmp.save()
                completed &= tmp.aceptado
        titulo = "Propuesta de {} {}".format(
            request.user.get_full_name(),
            "aceptada" if completed else "actualizada"
        )
        categoria = "Propuesta {}".format(
            "aceptada" if completed else "actualizada"
        )
        user = None
        if (prop.envio_comprador):
            user=negocio.comprador.persona.user
        else:
            user=negocio.vendedor.persona.user
        notif = Notificacion(
            titulo=titulo,
            categoria=categoria,
            hyperlink=reverse('negocio', args=[negocio.id,]),
            user=user
        )
        notif.save()
        return render(request, 'negocio.html')


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

def get_from_tuple(my_tuple, value):
    ret = ""
    for (x,y) in my_tuple:
        if y==value:
            ret = x
    return ret