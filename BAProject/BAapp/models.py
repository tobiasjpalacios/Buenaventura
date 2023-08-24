# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator 
from .choices import *
from .utils.fulltext import SearchManager
from .utils.email_send import email_send
from django.db.models import signals
from django.dispatch import dispatcher
from django.urls import reverse
from django.utils import formats
from django.contrib.sites.models import Site
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

class Empresa(models.Model):
    objects = SearchManager()
    razon_social = models.CharField(max_length=50, unique=True)
    nombre_comercial = models.CharField(max_length=50, blank=True, null=True, unique=True)
    cuit = models.CharField(max_length=14, blank=True, null=True, unique=True)
    ingresos_brutos = models.CharField(max_length=255, blank=True, null=True)
    fecha_exclusion = models.DateField(null=True, blank=True)
    categoria_iva = models.CharField(
        max_length=25, 
        choices=IVA_CHOICES,
        blank=True,
        null=True)
    domicilio_fiscal = models.CharField(max_length=255, blank=True, null=True)
    retenciones = models.ManyToManyField("Retencion", blank=True)

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
        null=True,
        blank=True,
        related_name="articulos")

    class Meta:
        search_fields = ('marca','ingrediente','concentracion')

    def __str__(self):
        if self.empresa != None:
            return '{} {}'.format(self.ingrediente, self.empresa.nombre_comercial)
        else:
            return self.ingrediente
    
    def clean(self):
        articulos = Articulo.objects.all()

        for articulo in articulos:
            if articulo.ingrediente == self.ingrediente and articulo.empresa == self.empresa:
                raise ValidationError(f'La empresa {self.empresa} ya posee el ingrediente {self.ingrediente}')


class Negocio(models.Model):
    comprador = models.ForeignKey(
        "MyUser",
        related_name='comprador',
        limit_choices_to={'clase': "Comprador"},
        on_delete=models.DO_NOTHING
    )

    vendedor = models.ForeignKey(
        "MyUser",
        related_name='vendedor',
        limit_choices_to={'clase': "Vendedor"},
        on_delete=models.DO_NOTHING,
        null=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    last_modified = models.DateTimeField(
        auto_now=True
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
    estado = models.CharField(
        max_length=22,
        choices=ESTADO_DE_NEGOCIO_CHOICES,
        blank=True,
        null=True,
        default=None 
    )
    id_de_neg = models.IntegerField(
        default=1
    )

    def __str__(self):
        return "Negocio: {}".format(self.timestamp)

    def get_id_de_neg(self):
        return f"BVi-{self.id_de_neg}"


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
        total = 0.0
        for item in self.items.all():
            total += item.precio_venta * item.cantidad
        return total

    def calcularTasa(self):
        tasa = 0.0
        for item in self.items.all():
            if item.tasa:
                cur_precio = item.precio_venta * item.cantidad
                tasa += ((cur_precio / 100) * float(item.tasa))
        return tasa

    def calcularTotal(self):
        return self.calcularPrecio() + self.calcularTasa()

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
        return self.nombre

class ItemPropuesta(models.Model):
    articulo = models.ForeignKey(
        "Articulo", 
        null=False, 
        on_delete=models.DO_NOTHING)
    proveedor = models.ForeignKey(
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    propuesta = models.ForeignKey(
        "Propuesta", 
        related_name="items",
        on_delete=models.CASCADE
    )
    cantidad = models.FloatField(
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

    # tasa = models.CharField(
    #     max_length=15,
    #     choices=TASA_CHOICES,
    #     blank=True,
    #     null=True
    #     )

    tasa = models.DecimalField(
                max_digits=4, 
                decimal_places=2, 
                validators=[
                        MaxValueValidator(100),
                        MinValueValidator(0)],
                default=1,
                blank=True,
                null=True,
                verbose_name='Tasa Mensual'
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
        "MyUser",
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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
        "MyUser", 
        limit_choices_to={'clase': "Proveedor"},
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


class MyUserManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password, clase, empresa, fecha_nacimiento, sexo, dni, telefono, domicilio):
        if not email:
            raise ValueError('Los usuarios deben tener un email')
        if not password:
            raise ValueError('Los usuarios deben tener una contraseña')
        user_obj = self.model(
            email = self.normalize_email(email),
            nombre = nombre,
            apellido = apellido,
            clase = clase,
            empresa = empresa,
            fecha_nacimiento = fecha_nacimiento,
            sexo = sexo,
            dni = dni,
            telefono = telefono,
            domicilio = domicilio
            )
        user_obj.set_password(password)
        user_obj.is_staff = False
        user_obj.is_superuser = False
        user_obj.save(using=self.db)
        return user_obj
    def create_superuser(self, email, password = None):
        user_obj = self.model(
            email = self.normalize_email(email))
        user_obj.set_password(password)
        user_obj.is_staff = True
        user_obj.is_superuser = True
        user_obj.save(using=self.db)
        return user_obj


class MyUser(AbstractBaseUser, PermissionsMixin):
    
    objects = MyUserManager()
    objs = MyUserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    clases = [
        ('Administrador', 'Administrador'),
        ('Comprador', 'Comprador'),
        ('Vendedor', 'Vendedor'),
        ('Proveedor', 'Proveedor'),
        ('Gerente', 'Gerente'),
        ('Logistica', 'Logistica')]

    nombre = models.CharField(max_length=50, blank=False)
    apellido = models.CharField(max_length=50, blank=False)
    email = models.EmailField(_('email address'), unique = True)
    clase = models.CharField(null=True, max_length=13, choices=clases)

    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(null=True, blank=True, max_length=6, choices=GENERO_CHOICES)
    dni = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(99999999)])
    telefono = models.CharField(null=True, blank=True, max_length=10)
    domicilio = models.CharField(null=True, blank=True, max_length=255)

    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        )

    is_superuser = models.BooleanField(
        _('superuser status'),
        default=True,
        help_text=_('Puede loggearse en el administrador y dar permisos a otros usuarios.'),
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Puede loggearse en el administrador.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Quitar este parámetro en lugar de borrar cuentas'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return '{} {}'.format(self.nombre, self.apellido)

    def get_clase(self):
        """
        Return the clase.
        """
        return self.clase

    def get_short_name(self):
        """Return the email of the user."""
        return self.email

    def get_razon_social(self):
        """Return the empresa__razon_social of the user."""
        return '{}'.format(self.empresa.razon_social)

# sistema de permisos
def set_perms(sender, instance, created, **kwargs):
    perms_name = ["logentry", "group", "permission", "negocio", "itempropuesta", "propuesta", "presupuesto", "contenttype", "session", "site", "myuser"]
    if instance.is_staff:
        permissions = Permission.objects.exclude(content_type__model__in=perms_name)
        instance.user_permissions.set(permissions)
    else:
        instance.user_permissions.clear()


# mandar email cada vez que se crea una notificacion (a excepcion de nuevos presupuestos y nuevos negocios)
# NOTE: comentado temporalmente
# @receiver(post_save, sender=Notificacion, dispatch_uid="send_email_notification")
def send_email_notification(sender, instance, **kwargs):
    if instance.titulo is not None and "Presupuesto" not in instance.titulo:
        if instance.descripcion is not None:
            pre_text = instance.descripcion
        else:
            pre_text = instance.titulo

        subject = instance.titulo
        fecha = formats.date_format(instance.timestamp, "SHORT_DATE_FORMAT")
        hora = formats.time_format(instance.timestamp, "TIME_FORMAT")
        formatted_timestamp = f"{fecha} a las {hora} hs"
        text = f"{pre_text}. Recibido el día {formatted_timestamp}."
        categoria = f"{instance.categoria}".lower()
        # agrega "s" al final a categoria en caso de ser vencimientos o presupuestos
        categoria = categoria + "s" if instance.categoria != "Logistica" else categoria
        protocol = "https://"
        domain = Site.objects.get_current().domain
        url =  protocol + domain + reverse(categoria)
        to = [instance.user.email]
        context = {'titulo' : subject, 'texto' : text, 'url' : url, 'categoria' : categoria}

        email_send(subject, to, 'email/notificacion.txt', 'email/notificacion.html', context)

signals.post_save.connect(set_perms, sender = MyUser)
# NOTE: comentado temporalmente
# post_save.connect(send_email_notification, sender = Notificacion)


def negocio_create_id_de_neg(sender, instance, created, *args, **kwargs):
    if created:
        with transaction.atomic():
            id_de_neg = 2000
            
            negocios = Negocio.objects.all().order_by('-id')
            
            try:
                last_negocio = negocios[1]
                id_de_neg = last_negocio.id_de_neg + 1
            except IndexError:
                pass

            instance.id_de_neg = id_de_neg
            instance.save(update_fields=["id_de_neg"])


signals.post_save.connect(negocio_create_id_de_neg, sender = Negocio)