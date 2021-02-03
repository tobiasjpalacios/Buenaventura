# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib import admin

from .choices import *

class Persona(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING)
    fecha_nacimiento = models.DateField(null=False)
    sexo = models.CharField(max_length=6, choices=GENERO_CHOICES)
    telefono = models.ForeignKey(
        "Telefono", 
        null = False, 
        on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)


class Vendedor(models.Model):
    persona = models.ForeignKey(
        "Persona",
        on_delete=models.DO_NOTHING)

    def __str__(self):
        return 'Vendedor {}'.format(str(self.persona))


class Empleado(models.Model):
    persona = models.ForeignKey(
        "Persona",
        on_delete=models.DO_NOTHING)
    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{} {} - {}".format(
            self.__class__.__name__, 
            self.persona, self.empresa)

    class Meta():
        abstract = True


class Comprador(Empleado):
    class Meta():
        default_related_name = "compradores"


class Gerente(Empleado):
    class Meta():
        default_related_name = "gerentes"


class Proveedor(Empleado):
    class Meta():
        default_related_name = "proveedores"


class Empresa(models.Model):
    razon_social = models.CharField(max_length=50)
    nombre_comercial = models.CharField(max_length=50, blank=True, null=True)
    cuit = models.CharField(max_length=14, blank=True, null=True)
    ingresos_brutos = models.CharField(max_length=9, blank=True, null=True)
    fecha_exclusion = models.DateField(null=True, blank=True)
    categoria_iva = models.CharField(
        max_length=25, 
        choices=IVA_CHOICES,
        blank=True,
        null=True)
    domicilio_fiscal = models.CharField(max_length=255, blank=True, null=True)
    retenciones = models.ManyToManyField("Retencion")

    def __str__(self):
        return "{}".format(self.razon_social)


class Retencion(models.Model):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return "{}".format(self.name)


class Domicilio(models.Model):  
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.direccion


class DomicilioPostal(models.Model):
    Empresa = models.ForeignKey(
        "Empresa", 
        null=False, 
        on_delete=models.CASCADE,
        related_name="domicilios_postal")
    Domicilio = models.OneToOneField(
        "Domicilio", 
        null = False, 
        on_delete=models.DO_NOTHING)


class DomicilioPersona(models.Model):
    Persona = models.ForeignKey(
        "Persona",
        null=False,
        on_delete=models.CASCADE,
        related_name="domicilio")
    Domicilio = models.OneToOneField(
        "Domicilio", 
        null = False, 
        on_delete=models.DO_NOTHING)


class Telefono(models.Model):
    numero = models.IntegerField()

    def __str__(self):
        return str(self.numero)


class Articulo(models.Model):
    marca = models.CharField(max_length=50, null=False, unique=True)
    ingrediente = models.CharField(max_length=100, null=False)
    concentracion = models.CharField(max_length=50)
    banda_toxicologica = models.CharField(
        max_length=50,
        choices=BANDA_TOXICOLOGICA_CHOICES)
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    unidad =  models.CharField(max_length=50, null=False)
    formulacion = models.CharField(max_length=20, null=False)
    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.DO_NOTHING,
        related_name="articulos")

    def __str__(self):
        return 'Articulo: {}'.format(self.marca)


class Negocio(models.Model):
    comprador = models.ForeignKey(
        "Comprador", 
        on_delete=models.DO_NOTHING)
    vendedor = models.ForeignKey(
        "Vendedor",
        on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Negocio: {}".format(self.timestamp)

    
class Propuesta(models.Model):
    negocio = models.ForeignKey(
        "Negocio",
        related_name="propuestas",
        on_delete=models.DO_NOTHING)
    envio_comprador = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    observaciones = models.CharField(max_length=300, blank=True)
    visto = models.BooleanField(default=False)
     
    def calcularPrecio(self):
        total = 0
        for item in self.items.all():
            total += item.precio * item.cantidad
        return total

    def calcularDiferencias(self, prop2):
        diffs = []
        for item in self.items.all():
            counter = prop2.items.get(articulo=item.articulo)
            diff = counter.calcularDiferencias(counter)
            if (diff):
                diffs.append(diff)

    def __str__(self):
        return 'Propuesta: {}'.format(
            self.id)
            

class ItemPropuesta(models.Model):
    articulo = models.ForeignKey(
        "Articulo", 
        null=False, 
        on_delete=models.DO_NOTHING)
    distribuidor = models.ForeignKey(
        "Empresa",
        null=True,  
        on_delete=models.DO_NOTHING)
    propuesta = models.ForeignKey(
        "Propuesta", 
        related_name="items",
        null=True, 
        on_delete=models.DO_NOTHING)
    tipo_de_operacion = models.CharField(max_length=255)
    cantidad = models.IntegerField(null=True, blank=True)
    precio = models.FloatField(null=True, blank=True)
    fecha_entrega = models.DateField()
    divisa = models.CharField(
        max_length=40, 
        choices=DIVISA_CHOICES,
        blank=True, null=True)
    destino = models.ForeignKey(
        "Domicilio", 
        null=True, 
        on_delete=models.DO_NOTHING)
    fecha_pago = models.DateField()
    tipo_pago = models.CharField(max_length=40)
    disponibilidad = models.BooleanField()
    fecha_disponibilidad = models.DateField(blank=True, null=True)
    aceptado = models.BooleanField()

    def calcularDiferencias(self, item2):
        dont = ('id','propuesta')
        diff = []
        if (not isinstance(item2, self.__class__)):
            raise TypeError("La comparacion debe ser entre items.")
        if (self.articulo != item2.articulo):
            return False
        fields = self._meta.get_fields()
        for f in fields:
            field = f.name
            if (not field in dont 
                and getattr(self, field) != getattr(item2, field)):
                diff.append(field)
        return diff

    def __str__(self):
        return 'Item: {} - Cantidad: {} - Precio: $ {}'.format(
            self.articulo.marca, 
            self.cantidad, 
            self.precio)


class Financiacion(models.Model):
    condicion = models.BooleanField()
    tasa = models.IntegerField(null = True)
    condicion_comercial = models.CharField(max_length=255)


class Presupuesto(models.Model):
    propuesta = models.ForeignKey(
        "Propuesta", 
        null=False, 
        on_delete=models.DO_NOTHING)
    area = models.CharField(max_length=50, null=False)
    fecha = models.DateField(auto_now_add=True)
    cobrado = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=300,null=False)
    visualizacion = models.BooleanField()

    def __str__(self):
        return 'Propuesta: {}'.format(self.propuesta.id)

    def total(self):
        return propuesta.calcularPrecio()
