from django.core.management.base import BaseCommand
from BAapp.models import ItemPropuesta
from BAapp.utils.date_parser import date_parser

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        items = ItemPropuesta.objects.all()
        
        for item in items:
            try:
                item.fecha_pago_date = date_parser(item.fecha_pago_str)
                item.save(update_fields=['fecha_pago_date'])
            except ValueError:
                pass