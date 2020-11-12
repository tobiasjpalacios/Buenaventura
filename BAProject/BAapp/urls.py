from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from BAapp.views import *


urlpatterns = [
    path('', landing_page, name='home'),
    path('administrar/', admin, name="admin"),

    path('clientes/', ListClienteView.as_view(), name="mostrar_clientes"),
    path('cliente/<int:pk>', ClienteView.as_view(), name="cliente"),
    path('cliente/', ClienteView.as_view(), name="registrar_cliente"),
    path('eliminarCliente/<str:pk>', eliminar_cliente, name="eliminar_cliente"),
    
    path('proveedores/', ListProveedorView.as_view(), name = "mostrar_proveedores"),
    path('proveedor/<int:pk>', ProveedorView.as_view(), name="proveedor"),
    path('crearProveedor/', ProveedorView.as_view(), name="crear_proveedor"),
]