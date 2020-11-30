# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib import admin

from .choices import *

class Persona(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    dni = models.IntegerField()
    fecha_nacimiento = models.DateField(null=False)
    sexo = models.CharField('Sexo', max_length=6, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=99, null=False)
    cuil_cuit = models.IntegerField(null=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)


class Cliente(Persona):
    codigo = models.IntegerField(null=False)
    categoria_iva = models.CharField(
        max_length=25, 
        choices=IVA_CHOICES)
    cuenta_contable = models.IntegerField(null=False)

    def __str__(self):
        return 'Cliente {} {}'.format(
            self.apellido, 
            self.nombre)


class Vendedor(Persona):
    fecha_ingreso = models.DateTimeField(null=False)
    fecha_egreso = models.DateTimeField()

    def __str__(self):
        return 'Vendedor {}'.format(str(super()))


#Aca falta que nos pasen los datos de lo que tiene un Proveedor 
#Con Proveedor me refiero a la entidad que tiene los productos, se 
# confunde el nombre por eso le puse EmpresaProveedor
#Cambienlo a cualquiera solo lo dejo para que lo puedan distinguir
class EmpresaProveedor(models.Model):
    nombre = models.CharField(max_length=50,null=False) 

    def __str__(self):
        return "Empresa {}".format(
            self.nombre)
    
class Proveedor(Persona):
    #Estos campos los comente pq no corresponden a esta tabla
    #Son una mezcla de ORganizacion transaccion y persona que emplea el rol de proveedor 
    """
    codigo = models.IntegerField(null=False)
    fax = models.CharField(max_length=50,null=False)
    codigo_cta = models.IntegerField(null=False)
    saldo_inicial = models.FloatField(null=False)
    alicuota = models.FloatField(null=False)
    sujeto_retencion = models.CharField(max_length=15, choices=RET_GANANCIA_CHOICES)
    categoria_iva = models.CharField('Categoria Iva', max_length=25, choices=IVA_CHOICES)
    desde_iibb = models.FloatField(null=False)
    hasta_iibb = models.FloatField(null=False)
    moneda = models.CharField(max_length=50,null=False)
    numero_cai = models.IntegerField(null=False)
    vencimiento_cai = models.DateTimeField(null=False)
    observaciones = models.CharField(max_length=50,null=False)
    """
    empresa = models.ForeignKey(EmpresaProveedor, null=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'Proveedor {} {} - Empresa {}'.format(
            self.apellido, 
            self.nombre, 
            self.empresa.nombre)


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE)
    nombre_articulo = models.CharField(max_length=50, null=False)
    precio_max = models.FloatField(null=False)
    fecha = models.DateTimeField(null=False)

    def __str__(self):
        return 'Pedido Nro: {} - Cliente {} {}'.format(
            self.id, 
            self.cliente.apellido, 
            self.cliente.nombre)


class Articulo(models.Model):
    proveedor = models.ForeignKey(EmpresaProveedor, null=False, on_delete=models.CASCADE)
    codigo_rubro = models.CharField(max_length=50, null=False)
    codigo_subrubro = models.CharField(max_length=50, null=False)
    codigo_articulo = models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=50, null=False)
    unidad_de =  models.CharField(max_length=20, choices=UNIDAD_CHOICES)
    precio_compra = models.FloatField(null=False)
    rubro = models.CharField(max_length=50, null=False)
    subrubro = models.CharField(max_length=50, null=False)

    def __str__(self):
        return 'Articulo: {}'.format(self.codigo_articulo)

    
class Propuesta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None)
    proveedor = models.ForeignKey(EmpresaProveedor, on_delete=models.CASCADE)
    items = models.ManyToManyField(Articulo, through="ItemPropuesta")
    divisa = models.CharField(max_length=40, default=None, choices=DIVISA_CHOICES)
    tasa = models.IntegerField(default=0, null=False)
    precio_venta = models.IntegerField(null=False, default=None)
    condicion_plazo = models.CharField(max_length=40, default=None)
    fecha_entrega = models.DateField(null=False)
    fecha_creacion = models.DateField(auto_now=True)
    lugar_entrega = models.CharField(max_length=40)
    observaciones = models.CharField(max_length=300, null=False)
     
    def calcularPrecio(self):
        total = 0
        for item in self.items.all():
            total += item.precio * item.cantidad
        return total
    
    def __str__(self):
        return 'Propuesta Nro: {} - Cliente {} {} - Articulo {}'.format(
            self.id, 
            self.cliente.apellido, 
            self.cliente.nombre, 
            self.articulo.codigo_articulo)

class ItemPropuesta(models.Model):
    articulo = models.ForeignKey(Articulo, null=False, on_delete=models.DO_NOTHING)
    propuesta = models.ForeignKey(Propuesta, null=False, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField(null=False)
    precio = models.FloatField(null=False)
    
    def __str__(self):
        return 'Item: {} - Cantidad: {} - Precio: $ {}'.format(
            self.articulo.codigo_articulo, 
            self.cantidad, 
            self.precio)


class Presupuesto(models.Model):
    propuesta = models.ForeignKey(Propuesta, null=False, on_delete=models.CASCADE)
    area = models.CharField(max_length=50, null=False)
    fecha = models.DateField(auto_now_add=True)
    razon_social = models.CharField(max_length=30, null=False)
    mes_de_pago = models.DateField(null=False)
    cobrado = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=300,null=False)

    def __str__(self):
        return 'Propuesta: {} - Monto: {}'.format(self.propuesta.id, self.total)

    def total(self):
        return propuesta.calcularPrecio()

class ItemPropuestaInline(admin.TabularInline):
    model = ItemPropuesta
    extra = 1

class PropuestaAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)

class ArticuloAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)