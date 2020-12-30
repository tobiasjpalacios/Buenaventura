from django.contrib import admin
from .models import *
# Register your models here.

class ItemPropuestaInline(admin.TabularInline):
    model = ItemPropuesta
    extra = 1

class PropuestaAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)

class ArticuloAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Presupuesto)
admin.site.register(Propuesta, PropuestaAdmin)
admin.site.register(Vendedor)
admin.site.register(Empresa)
admin.site.register(Retencion)
admin.site.register(Domicilio)
admin.site.register(DomicilioPostal)
admin.site.register(Telefono)
admin.site.register(Gerente)
admin.site.register(ItemPropuesta)
admin.site.register(Financiacion)
