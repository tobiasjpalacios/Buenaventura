from django.contrib import admin
from .models import *


class ItemPropuestaInline(admin.TabularInline):
    model = ItemPropuesta
    extra = 1

class PropuestaAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)

class ArticuloAdmin(admin.ModelAdmin):
    # inlines = (ItemPropuestaInline,)
    list_filter = ('banda_toxicologica', 'marca', 'empresa')
    list_display = ('ingrediente', 'marca','empresa',)
    search_fields = ['marca','empresa', ]
    ordering = ["ingrediente"]

class FacturaAdmin(admin.ModelAdmin):
    list_display  = ('fecha_emision','documento')

class NegocioAdmin(admin.ModelAdmin):
    list_display = ('id_de_neg', 'fecha_cierre')

admin.site.register(Comprador)
admin.site.register(Logistica)
admin.site.register(Administrador)
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
admin.site.register(Negocio, NegocioAdmin)
admin.site.register(Persona)
admin.site.register(TipoPago)
admin.site.register(Notificacion)
admin.site.register(Factura, FacturaAdmin)
admin.site.register(Remito)
admin.site.register(OrdenDeCompra)
admin.site.register(OrdenDePago)
admin.site.register(ConstanciaRentencion)
admin.site.register(Recibo)
admin.site.register(Cheque)
admin.site.register(CuentaCorriente)
admin.site.register(FacturaComision)
admin.site.register(Nota)