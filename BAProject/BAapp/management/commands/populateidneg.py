from django.core.management.base import BaseCommand
from BAapp.models import Negocio

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        negocios = Negocio.objects.all().order_by('id')
        count = 2000

        for negocio in negocios:
            negocio.id_de_neg = count
            count += 1
            negocio.save(update_fields=["id_de_neg"])