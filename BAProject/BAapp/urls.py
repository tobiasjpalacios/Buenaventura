from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from BAapp.views import *


urlpatterns = [
    path('', landing_page, name='home'),
    path('administrar/', admin, name="admin"),
    path('propuesta/', propuesta, name="propuesta"),
    path('testeo/', testeo, name="testeo"),

    path('clientes/', ListClienteView.as_view(), name="mostrar_clientes"),
    path('cliente/<int:pk>', ClienteView.as_view(), name="cliente"),
    path('cliente/', ClienteView.as_view(), name="registrar_cliente"),
        
    path('proveedores/', ListProveedorView.as_view(), name = "mostrar_proveedores"),
    path('proveedor/<int:pk>', ProveedorView.as_view(), name="proveedor"),
    path('proveedor/', ProveedorView.as_view(), name="crear_proveedor"),

    path('articulos/', ListArticuloView.as_view(), name = "mostrar_articulos"),
    path('articulo/<int:pk>', ArticuloView.as_view(), name="articulo"),
    path('articulo/', ArticuloView.as_view(), name="crear_articulo"),

    path('presupuestos/', ListPresupuestoView.as_view(), name = "mostrar_presupuestos"),
    path('presupuesto/<int:pk>', PresupuestoView.as_view(), name="presupuesto"),
    path('presupuesto/', PresupuestoView.as_view(), name="crear_presupuesto"),


]
