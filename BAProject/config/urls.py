"""BAProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from BAapp.views import *

urlpatterns = [
    path('', landing_page, name='home'),
    path('admin/', admin.site.urls),
    path('crearProveedor/', crear_proveedor, name = "crear_proveedor"),
    path('logout/', logout_user, name = "logout"),
    path('login/', login_user, name = "login"),
    path('registrarCliente/', registrar_cliente, name="registrar_cliente"),
    path('clientes/', mostrar_clientes, name="mostrar_clientes"),
    path('modificarCliente/<str:pk>', modificar_clientes, name="modificar_clientes"),
    path('eliminarCliente/<str:pk>', eliminar_cliente, name="eliminar_cliente"),
]
