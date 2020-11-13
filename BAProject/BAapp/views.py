from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout

from django.views import View

from .forms import *
from .models import *


def landing_page(request):
	return render(request, 'Principal.html')


class ProveedorView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": ProveedorForm()}
        if ("pk" in kwargs):
            context["proveedor"] = Proveedor.objects.get(pk=kwargs["pk"])
            context["form"] = ProveedorForm(instance=context["proveedor"])
        return render(request, 'proveedor.html', context)

    def post(self, request, *args, **kwargs):
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    def put(self, request, *args, **kwargs):
        proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        form = ProveedorForm(request.POST or None, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('/proveedores')

    def delete(self, request, *args, **kwargs):
        proveedor = Proveedor.objects.get(pk=kwargs["pk"])
        proveedor.delete()
        return HttpResponse(code=200)

class ListProveedorView(View):
    def get(self, request, *args, **kwargs):
        all_proveedores = Proveedor.objects.all()
        return render(request, 'consultar_proveedor.html', {'proveedores':all_proveedores})    


class ListClienteView(View):
    def get(self, request, *args, **kwargs):
        all_clientes = Cliente.objects.all()
        return render(request, 'consultar_cliente.html', {'clientes':all_clientes})    


class ClienteView(View):
    def get(self, request, *args, **kwargs):
        context = {
        "form": ClienteForm()}
        if ("pk" in kwargs):
            context["cliente"] = Cliente.objects.get(pk=kwargs["pk"])
            context["form"] = ClienteForm(instance=context["cliente"])
        return render(request, 'cliente.html', context)

    def post(self, request, *args, **kwargs):
        cliente = None
        if ("pk" in kwargs):
            cliente = Cliente.objects.get(pk=kwargs["pk"])
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return redirect("cliente", pk=cliente.pk)
        return render(request, 'cliente.html', context={"form":form})

    def delete(self, request, *args, **kwargs):
        cliente = Cliente.objects.get(pk=kwargs["pk"])
        cliente.delete()
        return HttpResponse(status=200)

# def modificar_clientes(request, pk):
#     cliente = Cliente.objects.get(pk=pk)
#     form = ClienteForm( instance = cliente)
#     if request.method == 'POST':
#         form = ClienteForm(request.POST or None, instance=cliente)
#         if form.is_valid():
#             form.save()
#             return redirect('/clientes')
#     context = {'form':form, 'cliente':cliente}
#     return render(request, 'modificar_clientes.html', context)

def eliminar_cliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('/clientes')
    context = {'cliente':cliente}
    return render(request, 'eliminar_cliente.html', context)

def admin(request):
    return render(request,'admin.html')