# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator 
from .choices import *
from .utils.fulltext import SearchManager
from django.db.models.signals import post_save
from django.dispatch import receiver

class Persona(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING, null=True)
    fecha_nacimiento = models.DateField(null=False)
    sexo = models.CharField(max_length=6, choices=GENERO_CHOICES)
    dni = models.PositiveIntegerField(null=True ,validators=[MinValueValidator(1), MaxValueValidator(99999999)])
    telefono = models.ForeignKey(
        "Telefono", 
        null=False, 
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


class Proveedor(models.Model):
    persona = models.ForeignKey("Persona",on_delete=models.DO_NOTHING)
    empresa = models.ManyToManyField("Empresa")

    def __str__(self):
        return "{} {} ".format(self.persona.user.last_name, self.persona.user.first_name)

class Logistica(Empleado):
    class Meta():
        default_related_name = "logisticas"
    
class Administrador(Empleado):
    class Meta():
        default_related_name = "administradores"


class Empresa(models.Model):
    objects = SearchManager()
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

    class Meta:
        search_fields = (
            'razon_social',
            'nombre_comercial',
            'cuit',
            'categoria_iva',
        )

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
        null=False, 
        on_delete=models.DO_NOTHING)


class DomicilioPersona(models.Model):
    Persona = models.ForeignKey(
        "Persona",
        null=False,
        on_delete=models.CASCADE,
        related_name="domicilio")
    Domicilio = models.OneToOneField(
        "Domicilio", 
        null=False, 
        on_delete=models.DO_NOTHING)


class Telefono(models.Model):
    numero = models.IntegerField()

    def __str__(self):
        return str(self.numero)


class Articulo(models.Model):
    objects = SearchManager()
    marca = models.CharField(max_length=50, null=False)
    ingrediente = models.CharField(max_length=200, null=False)
    concentracion = models.CharField(max_length=50, null=True)
    banda_toxicologica = models.CharField(
        max_length=50,
        choices=BANDA_TOXICOLOGICA_CHOICES, null=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    unidad =  models.CharField(max_length=50, null=True)
    formulacion = models.CharField(max_length=20, null=True)
    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.DO_NOTHING,
        related_name="articulos")

    class Meta:
        search_fields = ('marca','ingrediente','concentracion')

    def __str__(self):
        return '{} de {}'.format(self.ingrediente, self.marca)


class Negocio(models.Model):
    comprador = models.ForeignKey(
        "Comprador", 
        on_delete=models.DO_NOTHING
    )
    vendedor = models.ForeignKey(
        "Vendedor",
        on_delete=models.DO_NOTHING,
        null=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    fecha_cierre = models.DateTimeField(
        null=True, 
        blank=True
    )
    tipo_de_negocio = models.CharField(
        max_length=2,
        choices=TIPO_DE_NEGOCIO_CHOICES 
    )
    aprobado = models.BooleanField(default=False)
    cancelado = models.BooleanField(default=False)
    id_de_neg = models.CharField(
        "Identificador de negocio",
        max_length=255,
        null=True,
        blank=True,
        editable=False,
        default=""
    )

    def __str__(self):
        return "Negocio: {}".format(self.timestamp)


class Propuesta(models.Model):
    negocio = models.ForeignKey(
        "Negocio",
        related_name="propuestas",
        on_delete=models.DO_NOTHING)
    observaciones = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    envio_comprador = models.BooleanField()
    visto = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)
     
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
        return diffs

    def __str__(self):
        return 'Propuesta: {}'.format(
            self.id)
            
class TipoPago(models.Model):
    nombre = models.CharField(max_length=30, null=False)
    descripcion = models.CharField(max_length=100, null=True,blank=True)

    def __str__(self):
        return 'Tipo de pago: {}'.format(
            self.nombre)

class ItemPropuesta(models.Model):
    articulo = models.ForeignKey(
        "Articulo", 
        null=False, 
        on_delete=models.DO_NOTHING)
    proveedor = models.ForeignKey(
        "Proveedor",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    propuesta = models.ForeignKey(
        "Propuesta", 
        related_name="items",
        on_delete=models.CASCADE
    )
    cantidad = models.IntegerField(
        null=True, 
        blank=True
    )
    precio_venta = models.FloatField(
        null=True, 
        blank=True
    )
    precio_compra = models.FloatField(
        null=True, 
        blank=True
    )
    divisa = models.CharField(
        max_length=40, 
        choices=DIVISA_CHOICES,
        blank=True, 
        null=True
    )
    destino = models.CharField(
        max_length=255,
        null=True,
        default=""
    )
    fecha_entrega = models.CharField(
        null=True,
        blank=True,
        max_length=12
    )
    aceptado = models.BooleanField()
    pagado = models.BooleanField(default=False)
    fecha_pago = models.CharField(
        null=True,
        blank=True,
        max_length=12
    )
    fecha_real_pago = models.DateTimeField(
        null=True,
        blank=True
    )
    tipo_pago = models.ForeignKey(
            "TipoPago",
            null=True,
            blank = True,
            on_delete=models.DO_NOTHING,
        )
    tasa = models.CharField(
        max_length=15,
        choices=TASA_CHOICES,
        blank=True,
        null=True
        )
    fecha_salida_entrega = models.DateTimeField(
        null=True,
        blank=True
    )
    fecha_real_entrega = models.DateTimeField(
        null=True,
        blank=True
    )

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
        return 'Item: {} - Cantidad: {}'.format(
            self.articulo.marca, 
            self.cantidad)


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

class Notificacion(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    categoria = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    hyperlink = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING)
    visto = models.BooleanField(default=False)

    class Meta:
        ordering = ('-timestamp',)

class Factura(models.Model):
    #id 
    #emisor - usuario - proveedor
    #receptor - get_comprador()
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    fecha_vencimiento = models.DateField(null=False)
    
    numero_factura = models.IntegerField(null=False)
    
    proveedor = models.ForeignKey(
        "Proveedor", 
        null=False, 
        on_delete=models.DO_NOTHING)
    tipo_pago = models.ForeignKey(
            "TipoPago",
            null=False,
            blank = True,
            on_delete=models.DO_NOTHING,
        )
    monto = models.PositiveIntegerField(null=False ,validators=[MinValueValidator(1), MaxValueValidator(99999999)])

    documento = models.FileField(upload_to='media/facturas/%Y/%m/%d', null=False)

    class Meta():
        default_related_name = "facturas"

class Remito(models.Model):
    #emisor proveedor
    #cliente - get_comprador()
    #tienen q poder cargarlo los vendedores tmb
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    fecha_vencimiento = models.DateField(null=False)
    
    proveedor = models.ForeignKey(
        "Proveedor", 
        null=False, 
        on_delete=models.DO_NOTHING)
	#desc_productos 
    lote = models.CharField(max_length=255)
    observaciones = models.TextField(null=False)

    documento = models.FileField(upload_to='media/remitos/%Y/%m/%d', null=False)
    class Meta():
        default_related_name = "remitos"



class OrdenDeCompra(models.Model):
    #emisor: comprador
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    recibe_proveedor = models.ForeignKey(
        "Proveedor", 
        null=False, 
        on_delete=models.DO_NOTHING)

    documento = models.FileField(upload_to='media/ordenesCompras/%Y/%m/%d', null=False)
	
	
class OrdenDePago(models.Model): 
    #emisor: comprador
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    factura = models.ForeignKey(
        "Factura", 
        null=False, 
        on_delete=models.DO_NOTHING) 
    recibe_proveedor = models.ForeignKey(
        "Proveedor",
        null=False, 
        on_delete=models.DO_NOTHING)

    monto = models.PositiveIntegerField(null=False ,validators=[MinValueValidator(1), MaxValueValidator(99999999)])
    documento = models.FileField(upload_to='media/ordenesPagos/%Y/%m/%d', null=False)
   
	
class ConstanciaRentencion(models.Model):
    #emisor: comprador
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    recibe_proveedor = models.ForeignKey(
        "Proveedor",
        null=False, 
        on_delete=models.DO_NOTHING) 
    importe = models.FloatField()
    documento = models.FileField(upload_to='media/constanciasRetencion/%Y/%m/%d', null=False)
	#negocio(cliente-provedores-fecha)
	
class Recibo(models.Model):
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    recibe_proveedor = models.ForeignKey(
        "Proveedor",
        null=False, 
        on_delete=models.DO_NOTHING)
    monto = models.PositiveIntegerField(null=False ,validators=[MinValueValidator(1), MaxValueValidator(99999999)])
    documento = models.FileField(upload_to='media/recibos/%Y/%m/%d', null=False)
	#(recibe) cliente
	#proveedor a cliente 
	#items 
	
class Cheque(models.Model):
    #emite cliente
	#fecha subida 
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)
    fecha_emision = models.DateField(null=False)
    documento = models.FileField(upload_to='media/cheques/%Y/%m/%d', null=False)
    class Meta():
        default_related_name = "cheques"

class CuentaCorriente(models.Model):
	#emite proveedor
	#fecha subida 
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    documento = models.FileField(upload_to='media/cuentasCorriente/%Y/%m/%d', null=False)
    class Meta():
        default_related_name = "cuentas_corrientes"

class FacturaComision(models.Model):
	#carga vendedor()
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    recibe_proveedor = models.ForeignKey(
        "Proveedor",
        null=False, 
        on_delete=models.DO_NOTHING)
    documento = models.FileField(upload_to='media/facturasComision/%Y/%m/%d', null=False)
    class Meta():
        default_related_name = "facturas_comisiones"
	
class Nota(models.Model):
    #emite proveedor 
	#recibe get_comprador() 
	#nro_factura()
    negocio = models.ForeignKey(
        "Negocio", 
        null=False, 
        on_delete=models.DO_NOTHING)

    fecha_emision = models.DateField(null=False)
    tipo_nota = models.CharField(
        max_length=15,
        choices=TIPO_NOTA,
        null=False
        )
    documento = models.FileField(upload_to='media/notas/%Y/%m/%d', null=False)
    class Meta():
        default_related_name = "notas"