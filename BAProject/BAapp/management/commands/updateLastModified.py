from django.core.management.base import BaseCommand
from BAapp.models import Negocio, Propuesta

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        negocios = Negocio.objects.all()
        
        for negocio in negocios:
            try:
                propuesta = Propuesta.objects.filter(negocio=negocio).last()
                negocio.last_modified = propuesta.timestamp
                negocio.save()
            except AttributeError:
                print(f"Error en el negocio {negocio.get_id_de_neg()}. ¿No tiene propuestas?")