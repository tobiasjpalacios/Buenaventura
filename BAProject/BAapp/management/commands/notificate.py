from django.core.management.base import BaseCommand
from BAapp.models import Negocio, Propuesta
from BAapp.utils.negocios_helper import get_item_propuestas_vencidos_ayer, get_item_propuestas_proximos_a_vencer
from BAapp.utils.notificaciones import crear_notificacion
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.urls import reverse


def get_vencimiento_notificacion(fecha_pago):
    now = timezone.localtime(timezone.now()).date()
    diferencia = fecha_pago - now
    days = diferencia.days
    if days > 1:
        message = f"vence en {days} días"
    elif days == 1:
        message = "vence mañana"
    elif days < 1:
        message = "vence hoy"
    return message

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        negocios_cerrados_conf = Negocio.objects.filter(fecha_cierre__isnull=False).order_by('-timestamp')
        
        lista_vencidos = []
        lista_proximos = []
        
        for negocio in negocios_cerrados_conf:
            
            try:
                propuesta = Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').first()
            except Exception as e:
                print(e)
                
            item_propuestas_vencidos = get_item_propuestas_vencidos_ayer(propuesta.id)
            item_propuestas_proximos = get_item_propuestas_proximos_a_vencer(propuesta.id)
            
            lista_vencidos.extend(item_propuestas_vencidos)
            lista_proximos.extend(item_propuestas_proximos)
            
        for item_propuesta in lista_vencidos:
            categoria = "Vencimiento"
            vendedor = item_propuesta.propuesta.negocio.vendedor
            comprador = item_propuesta.propuesta.negocio.comprador
            hyperlink = reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg})
            # para vendedor
            crear_notificacion(
                titulo=f"Pago del artículo {item_propuesta.articulo} de {comprador.get_full_name()} vencido el {item_propuesta.fecha_pago_str}",
                categoria=categoria,
                hyperlink=hyperlink,
                user=vendedor
            )
            # para comprador
            crear_notificacion(
                titulo=f"Pago del artículo {item_propuesta.articulo} vencido el {item_propuesta.fecha_pago_str}",
                categoria=categoria,
                hyperlink=hyperlink,
                user=comprador
            )
            
        for item_propuesta in lista_proximos:
            categoria = "Vencimiento"
            vendedor = item_propuesta.propuesta.negocio.vendedor
            comprador = item_propuesta.propuesta.negocio.comprador
            hyperlink = reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg})
            # para vendedor
            crear_notificacion(
                titulo=f"Pago del artículo {item_propuesta.articulo} de {comprador.get_full_name()} {get_vencimiento_notificacion(item_propuesta.fecha_pago_date)}.",
                categoria=categoria,
                hyperlink=hyperlink,
                user=vendedor
            )
            # para comprador
            crear_notificacion(
                titulo=f"Pago del artículo {item_propuesta.articulo} {get_vencimiento_notificacion(item_propuesta.fecha_pago_date)}.",
                categoria=categoria,
                hyperlink=hyperlink,
                user=comprador
            )