from django.core.management.base import BaseCommand
from BAapp.models import Negocio, Propuesta
from BAapp.utils.negocios_helper import get_articulos_vencidos_ayer, get_articulos_proximos_a_vencer
from BAapp.utils.notificaciones import crear_notificacion
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone


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
                
            articulos_vencidos = get_articulos_vencidos_ayer(propuesta.id)
            articulos_proximos = get_articulos_proximos_a_vencer(propuesta.id)
            
            lista_vencidos.extend(articulos_vencidos)
            lista_proximos.extend(articulos_proximos)
            
        for articulo in lista_vencidos:
            categoria = "Vencimiento"
            vendedor = articulo.propuesta.negocio.vendedor
            comprador = articulo.propuesta.negocio.comprador
            # para vendedor
            crear_notificacion(
                titulo=f"Pago del artículo {articulo.articulo} de {comprador.get_full_name()} vencido el {articulo.fecha_pago_str}",
                categoria=categoria,
                hyperlink="",
                user=vendedor
            )
            # para comprador
            crear_notificacion(
                titulo=f"Pago del artículo {articulo.articulo} vencido el {articulo.fecha_pago_str}",
                categoria=categoria,
                hyperlink="",
                user=comprador
            )
            
        for articulo in lista_proximos:
            categoria = "Vencimiento"
            vendedor = articulo.propuesta.negocio.vendedor
            comprador = articulo.propuesta.negocio.comprador
            # para vendedor
            crear_notificacion(
                titulo=f"Pago del artículo {articulo.articulo} de {comprador.get_full_name()} {get_vencimiento_notificacion(articulo.fecha_pago_date)}.",
                categoria=categoria,
                hyperlink="",
                user=vendedor
            )
            # para comprador
            crear_notificacion(
                titulo=f"Pago del artículo {articulo.articulo} {get_vencimiento_notificacion(articulo.fecha_pago_date)}.",
                categoria=categoria,
                hyperlink="",
                user=comprador
            )