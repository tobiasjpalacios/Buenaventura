from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Articulo)
admin.site.register(Presupuesto)
admin.site.register(Propuesta)
admin.site.register(Pedido)
admin.site.register(Vendedor)