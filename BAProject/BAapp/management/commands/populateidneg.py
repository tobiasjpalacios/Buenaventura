from django.core.management.base import BaseCommand
from BAapp.models import Negocio

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        negocios = Negocio.objects.all().order_by('id')
        
        for count, negocio in enumerate(negocios):
            negocio.id_de_neg = count + 1
            negocio.save(update_fields=["id_de_neg"])