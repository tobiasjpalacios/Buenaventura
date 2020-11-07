from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import *
from .models import *


def landing_page(request):
	return render(request,'Principal.html')

def crear_proveedor(request):
    form = ProveedorForm()
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request,'crear_proveedor.html',{'form': form})

def registrar_cliente(request):
    form = ClienteForm()
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request, 'registrar_cliente.html', {'form':form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Password or Username incorrect, please try again.')
        return render(request, 'home')


def mostrar_clientes(request):
    all_clientes = Cliente.objects.all()
    return render(request, 'consultar_cliente.html', {'Clientes':all_clientes})    


def modificar_clientes(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    form = ClienteForm( instance = cliente)
    if request.method == 'POST':
        form = ClienteForm(request.POST or None, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('/clientes')
    context = {'form':form, 'cliente':cliente}
    return render(request, 'modificar_clientes.html', context)

def eliminar_cliente(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('/clientes')
    context = {'cliente':cliente}
    return render(request, 'eliminar_cliente.html', context)

def logout_user(request):
    logout(request)
    return redirect('/')
