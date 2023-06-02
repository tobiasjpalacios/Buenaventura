from django.core.management.base import BaseCommand
from BAapp.models import Negocio, Propuesta

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        negocio = Negocio.objects.all()

        for neg in negocio:
            if not neg.estado:
                prop = Propuesta.objects.filter(negocio=neg.id).last()
                if neg.aprobado:
                    neg.estado = "CONFIRMADO"
                elif neg.cancelado:
                    neg.estado = "CANCELADO"
                elif prop.envio_comprador:
                    neg.estado = "RECIBIDO"
                else:
                    neg.estado = "NEGOCIACION"
                neg.save()