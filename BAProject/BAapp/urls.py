from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from BAapp.views import *

apipatters = [
    path('articulos/',APIArticulos.as_view() , name="api_articulos"),
]

urlpatterns = [
    path('', landing_page, name='home'),
    path('administrar/', admin, name="admin"),
    path('testeo/', testeo, name="testeo"),
    path('chat/', chat, name="chat"),
    path('inicio/', inicio, name="inicio"),
    path('cliente/', cliente, name="Cliente"),
    path('vendedor/', vendedor, name="vendedor"),

    path('compradores/', ListCompradorView.as_view(), name="mostrar_compradores"),
    path('comprador/<int:pk>', CompradorView.as_view(), name="comprador"),
    path('comprador/', CompradorView.as_view(), name="registrar_comprador"),
        
    path('proveedores/', ListProveedorView.as_view(), name = "mostrar_proveedores"),
    path('proveedor/<int:pk>', ProveedorView.as_view(), name="proveedor"),
    path('proveedor/', ProveedorView.as_view(), name="crear_proveedor"),

    path('articulos/', ListArticuloView.as_view(), name = "mostrar_articulos"),
    path('articulo/<int:pk>', ArticuloView.as_view(), name="articulo"),
    path('articulo/', ArticuloView.as_view(), name="crear_articulo"),

    path('presupuestos/', ListPresupuestoView.as_view(), name = "mostrar_presupuestos"),
    path('presupuesto/<int:pk>', PresupuestoView.as_view(), name="presupuesto"),
    path('presupuesto/', PresupuestoView.as_view(), name="crear_presupuesto"),

    #path('propuesta/', ListPropuestaView.as_view(), name = "mostrar_propuestas"),
    path('propuesta/<int:pk>', PropuestaView.as_view(), name="propuesta"),
    path('propuesta/', PropuestaView.as_view(), name="crear_propuesta"),

    path('empresas/', ListEmpresaView.as_view(), name = "mostrar_empresas"),
    path('empresa/<int:pk>', EmpresaView.as_view(), name="empresa"),
    path('empresa/', EmpresaView.as_view(), name="registrar_empresa"),

    # crear propuestas

    path('api/', include(apipatters)),
    path('filterArticulo/<str:ingrediente>', filterArticulo, name="filterArticulo")
    
]
