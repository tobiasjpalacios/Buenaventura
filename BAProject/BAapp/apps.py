from django.apps import AppConfig

GRUPOS_USUARIO = (
    'Logistica',
    'Vendedor',
    'Proveedor',
    'Comprador',
    'Administracion',)

RET_GANANCIA_CHOICES = (
    'Arrendamiento',
    'Exento',
    'Honorarios',
    'Insumos',
    'Servicios',
    'Transporte',
)

class BaappConfig(AppConfig):
    name = 'BAapp'

    def ready(self):
        import sys

        from django.contrib.auth.models import Group, User

        from . import models
        from . import choices

        if ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            return 

        for g in GRUPOS_USUARIO:
            group, created = Group.objects.get_or_create(name=g)

        for i in RET_GANANCIA_CHOICES:
            ret, created = models.Retencion.objects.get_or_create(name=i)