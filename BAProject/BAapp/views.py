from django.shortcuts import render, redirect
from .forms import *
from .models import *

def landing_page(request):
	return render(request,'Principal.html')

def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_proveedor')
    else:
        form = ProveedorForm()
    return render(request,'crear_proveedor.html',{'form': form})
