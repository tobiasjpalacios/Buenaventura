from django.apps import AppConfig


class BaappConfig(AppConfig):
    name = 'BAapp'

    def ready(self):
        import sys

        from django.contrib.auth.models import Group, User

        from . import models

        if ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            return 

        logistica, created = Group.objects.get_or_create(name='Logistica')
        vendedor, created = Group.objects.get_or_create(name='Vendedor')
        proveedor, created = Group.objects.get_or_create(name='Proveedor')
        cliente, created = Group.objects.get_or_create(name='Cliente')
        administracion, created = Group.objects.get_or_create(name='Administracion')