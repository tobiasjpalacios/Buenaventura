# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

from .choices import *

class Persona(models.Model):
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    dni = models.IntegerField()
    email = models.EmailField(max_length=50, null=False)
    fecha_nacimiento = models.DateField(null=False)
    sexo = models.CharField('Sexo', max_length=6, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=99, null=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Cliente(Persona):
    codigo = models.IntegerField(null=False)
    cuil_cuit = models.IntegerField(null=False)
    categoria_iva = models.CharField('Categoria Iva', max_length=25, choices=IVA_CHOICES)
    cuenta_contable = models.IntegerField(null=False)

    def __str__(self):
        return '{} {}'.format(self.nombre, self.apellido)


class Vendedor(Persona):
    fecha_ingreso = models.DateTimeField(null=False)

    def __str__(self):
        return 'Vendedor {} {}'.format(self.apellido, self.nombre)


#Aca falta que nos pasen los datos de lo que tiene un Proveedor 
#Con Proveedor me refiero a la entidad que tiene los productos, se confunde el nombre por eso le puse EmpresaProveedor
#Cambienlo a cualquiera solo lo dejo para que lo puedan distinguir
class EmpresaProveedor():
    nombre = models.CharField(max_length=50,null=False) 
    
class Proveedor(Persona):
    #Estos campos los comente pq no corresponden a esta tabla
    #Son una mezcla de ORganizacion transaccion y persona que emplea el rol de proveedor 
    """
    codigo = models.IntegerField(null=False)
    fax = models.CharField(max_length=50,null=False)
    cuil_cuit = models.IntegerField(null=False)
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
        return 'Proveedor {} {} - Empresa {}'.format(self.apellido, self.nombre, self.empresa.nombre)


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE)
    nombre_articulo = models.CharField(max_length=50, null=False)
    precio_max = models.FloatField(null=False)
    fecha = models.DateTimeField(null=False)

    def __str__(self):
        return 'Pedido Nro: {} - Cliente {} {}'.format(self.id, self.cliente.apellido, self.cliente.nombre)


class Articulo(models.Model):
    proveedor = models.ForeignKey(Proveedor, null=False, on_delete=models.CASCADE)
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

class registroArticulo(models.Model):
    articulo = models.ForeignKey(Articulo, null=False, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False)
    precio = models.FloatField(null=False)
    
    def __str__(self):
        return 'Articulo: {} - Cantidad: {} - Precio: $ {}'.format(self.articulo.codigo_articulo, self.cantidad, self.precio)
    
class Propuesta(models.Model):
    #Aca tengo la duda de si es mejor seleccionar la persona que dio los datos sobre la disponibilidad de productos
    #O seleccionar la Empresa y a partir de eso el proveedor con el que se llego al acuerdo
    #Para mi es mejor la empresa y a partir de eso los empleados pero se lo dejo a ustedes que son los que lo van a programar
    proveedor = models.ForeignKey(Proveedor, null=False, on_delete=models.CASCADE)
    #Registro tiene que ser One To Many
    registro = models.ForeignKey(registroArticulo, null=False, on_delete=models.CASCADE)
    fecha_entrega = models.DateField(null=False)
    lugar_entrega = models.CharField(max_length=40)
    observaciones = models.CharField(max_length=300,null=False)
    aceptada = models.BooleanField()
    #El campo Fecha Creacion se me ocurrio como un extra para registrar cuando se realizo la Propuesta
    #No estaria de mas teniendo en cuenta que es un pedido formal pero si creen que es al pedo saquenlo.
    #fecha_creacion = models.DateField(null=False) 
    
    def __str__(self):
        return 'Propuesta Nro: {} - Vendedor {} {} - Articulo {}'.format(self.id, self.vendedor.apellido, self.vendedor.nombre, self.articulo.codigo_articulo)
    
    #Mi idea con este metodo era calcular el precio total de la Propuesta
    #Pero no esta aclarado si el precio es por Unidad de Articulo o el total del precio unitario por la cantidad
    #Cualquer cosa cambien la formula a: total += a.precio si el precio es respecto a la cantidad por precio unitario
    def calcularPrecio(self):
        total = 0
        for a in range(len(self.registro)):
            total += a.precio * a.cantidad
            
        return total


class Presupuesto(models.Model):
    propuesta = models.ForeignKey(Propuesta, null=False, on_delete=models.CASCADE)
    area = models.CharField(max_length=50, null=False)
    fecha = models.DateField(null=False)
    razon_social = models.CharField(max_length=30, null=False)
    total = models.FloatField(null=False)
    mes_de_pago = models.DateField(null=False)
    cobrado = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=300,null=False)

    def __str__(self):
        return 'Propuesta: {} - Monto: {}'.format(self.propuesta.id, self.total)