# -*- coding: utf-8 -*-
from django.db import models
from .choices import *
class Persona(models.Model):


    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    dni = models.IntegerField(primary_key=True)
    email = models.EmailField(max_length=50, null=False)
    fecha_nacimiento = models.DateTimeField(null=False)
    sexo = models.CharField('Sexo', max_length=6, choices=GENERO_CHOICES)
    telefono = models.IntegerField(null=False)

    class Meta:
        abstract = True

class Cliente(Persona):

    codigo = models.IntegerField(null=False)
    cuil_cuit = models.IntegerField(null=False)
    categoria_iva = models.CharField('Categoria Iva', max_length=15, choices=CATEGORIA_CHOICES)
    cuenta_contable = models.IntegerField(null=False)

    def __str__(self):
        return 'El Cliente {} {} con el Codigo {} posee la Categoria {}'.format(self.apellido, self.nombre, self.codigo, self.categoria_iva)

class Vendedor(Persona):
    fecha_ingreso = models.DateTimeField(null=False)

    def __str__(self):
        return 'Vendedor {} {}'.format(self.apellido, self.nombre)

class Proveedor(Persona):
    codigo = models.IntegerField(null=False)
    fax = models.CharField(max_length=50,null=False)
    cuil_cuit = models.IntegerField(null=False)
    codigo_cta = models.IntegerField(null=False)
    saldo_inicial = models.FloatField(null=False)
    alicuota = models.FloatField(null=False)
    #Sujeto de Retencion
    #Categoria
    desde_iibb = models.FloatField(null=False)
    hasta_iibb = models.FloatField(null=False)
    moneda = models.CharField(max_length=50,null=False)
    numero_cai = models.IntegerField(null=False)
    vencimiento_cai = models.DateTimeField(null=False)
    observaciones = models.CharField(max_length=50,null=False)

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE)
    nombre_articulo = models.CharField(max_length=50, null=False)
    precio_max = models.FloatField(null=False)
    fecha = models.DateTimeField(null=False)

    def __str__(self):
        return 'Pedido Nro: {} - Cliente {} {}'.format(self.id, self.apellido, self.nombre)

class Articulo(models.Model):
    proveedor = models.ForeignKey(Proveedor, null=False, on_delete=models.CASCADE)
    codigo_rubro = models.CharField(max_length=50, null=False)
    codigo_subrubro = models.CharField(max_length=50, null=False)
    codigo_articulo = models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=50, null=False)
    #unidad_de
    precio_compra = models.FloatField(null=False)
    rubro = models.CharField(max_length=50, null=False)
    subrubro = models.CharField(max_length=50, null=False)

    def __str__(self):
        return 'Articulo: {}'.format(self.codigo_articulo)

class Propuesta(models.Model):
    pedido = models.ForeignKey(Pedido, null=False, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, null=False, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, null=False, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False)
    comision_usd = models.FloatField(null=False)
    comision = models.FloatField(null=False)
    precio_venta = models.FloatField(null=False)
    aceptada = models.BooleanField()

    def __str__(self):
        return 'Propuesta Nro: {} - Vendedor {} {} - Articulo {}'.format(self.id, self.vendedor.apellido, self.vendedor.nombre, self.articulo.codigo_articulo)

class Presupuesto(models.Model):
    propuesta = models.ForeignKey(Propuesta, null=False, on_delete=models.CASCADE)
    area = models.CharField(max_length=50, null=False)
    fecha = models.DateTimeField(null=False)
    razon_social = models.CharField(max_length=30, null=False)
    total = models.FloatField(null=False)
    mes_de_pago = models.DateTimeField(null=False)
    #Cobrado
    observaciones = models.CharField(max_length=300,null=False)

    def __str__(self):
        return 'Propuesta: {} - Monto: {}'.format(self.propuesta.id, self.total)