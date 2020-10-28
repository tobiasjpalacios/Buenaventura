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

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('')
        else:
            messages.error(request, 'Password or Username incorrect, please try again.')
        return render(request, '')

def logout_user(request):
    logout(request)
    return redirect('/')
