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

from .forms import *
from .models import *
from .choices import DIVISA_CHOICES

def landing_page(request):
	return render(request, 'Principal.html')

def admin(request):
    return render(request,'admin.html')

def chat(request):
    return render(request,'chat.html')

def inicio(request):
    return render(request,'inicio.html')


def testeo(request):
    return render(request, 'testeo.html')

def cliente(request):
    return render(request, 'cliente.html')

def vendedor(request):
    return render(request, 'vendedor.html')


def carga_excel(request):
    return render(request, 'carga_excel.html')

class APIArticulos(View):
    def get(self,request):
        articulos = None
        if (request.GET.get('search', None)):
            words = request.GET['search'].split(" ")
            for i in range(len(words)):
                words[i] = "{}".format(words[i])
            searchStr = " ".join(words)
            articulos = Articulo.objects.search(searchStr)
        else:
            articulos = Articulo.objects.all()
        return JsonResponse(list(articulos.values("marca", "ingrediente","id")), safe=False)

    def post(self,request):
        data = json.loads(request.body.decode("utf-8"))
        for i in range(len(data)):
            actual = data[i]
            marca = actual.get("Marca")
            ingrediente = actual.get("Ingrediente")
            articulo = Articulo.objects.get(marca=marca, ingrediente=ingrediente)
            item = ItemPropuesta(
                articulo=articulo, 
                distribuidor=None,
                propuesta=None,
                tipo_de_operacion="",
                cantidad=actual.get("Cantidad"),
                precio=actual.get("Precio X unidad"),
                fecha_entrega= datetime.date.today(),
                divisa="",
                destino=None,
                fecha_pago=datetime.date.today(),
                tipo_pago="",
                disponibilidad=False,
                fecha_disponibilidad=datetime.date.today())
            item.save()
        return HttpResponse(status=200)

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
        negocio = Negocio.objects.get(pk=kwargs["pk"])
        data = negocio.propuestas.last()
        last = {
            'items': [],
            'observaciones': data.observaciones
        }
        for i in data.items.all():
            art = {
                'id': i.id,
                'articulo': i.articulo.id,
                'distribuidor': i.distribuidor.id,
                'cantidad': i.cantidad,
                'precio': i.precio,
                'divisa': i.divisa,
                'destino': i.destino.id,
                'aceptado': i.aceptado,
            }
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
        prop = Propuesta(
            negocio=negocio,
            observaciones=data["observaciones"],
            envio_comprador=request.user.groups.filter(name="comprador").exists()
        )
        prop.save()
        with transaction.atomic():
            for item in data["items"]:
                tmp = ItemPropuesta(
                    articulo=get_object_or_404(
                        Articulo, 
                        pk=item['articulo']
                    ),
                    distribuidor=get_object_or_404(
                        Empresa, 
                        pk=item['distribuidor']
                    ),
                    destino=get_object_or_404(
                        Domicilio,
                        pk=item['destino']
                    ),
                    propuesta=prop,
                    cantidad=item['cantidad'],
                    precio=item['precio'],
                    aceptado=item['aceptado']
                )
                tmp.save()
        return render(request, 'negocio.html')

    def delete(self, request, *args, **kwargs):
        return HttpResponse(code=200)


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