from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Presupuesto)
admin.site.register(Propuesta, PropuestaAdmin)
admin.site.register(Pedido)
admin.site.register(Vendedor)
admin.site.register(EmpresaProveedor)