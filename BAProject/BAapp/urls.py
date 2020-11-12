from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from BAapp.views import *


urlpatterns = [
    path('', landing_page, name='home'),
    path('crearProveedor/', crear_proveedor, name = "crear_proveedor"),
    path('clientes/', ListClienteView.as_view(), name="mostrar_clientes"),
    path('cliente/<int:pk>', ClienteView.as_view(), name="cliente"),
    path('cliente/', ClienteView.as_view(), name="registrar_cliente"),
    path('eliminarCliente/<str:pk>', eliminar_cliente, name="eliminar_cliente"),
]