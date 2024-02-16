from django.core.management.base import BaseCommand
from BAapp.models import Negocio, Propuesta, MyUser
from BAapp.utils.negocios_helper import get_vencidos_ayer_pago, get_proximos_vencer_pago, get_pago_estado, get_atrasados_ayer_entrega, get_a_tiempo_entrega, get_entrega_dias_restantes
from BAapp.utils.notificaciones import crear_notificaciones_usuarios
from django.utils import timezone
from django.urls import reverse


def notificate_pago():
    negocios_cerrados_conf = Negocio.objects.filter(fecha_cierre__isnull=False).order_by('-timestamp')
        
    lista_vencidos = []
    lista_proximos = []
    
    for negocio in negocios_cerrados_conf:
        
        try:
            propuesta = Propuesta.objects.filter(negocio=negocio).order_by('-timestamp').first()
        except Exception as e:
            print(e)
            
        item_propuestas_vencidos = get_vencidos_ayer_pago(propuesta)
        item_propuestas_proximos = get_proximos_vencer_pago(propuesta)
        
        lista_vencidos.extend(item_propuestas_vencidos)
        lista_proximos.extend(item_propuestas_proximos)
        
    for item_propuesta in lista_vencidos:
        vendedor = item_propuesta.propuesta.negocio.vendedor
        comprador = item_propuesta.propuesta.negocio.comprador
        proveedor = item_propuesta.proveedor
        users_list = [vendedor, comprador, proveedor]
        context = {
            "titulo": f"Pago del artículo {item_propuesta.articulo} de {comprador.get_full_name()} vencido el {item_propuesta.fecha_pago_str}",
            "categoria": "Vencimiento",
            "hyperlink": reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg}),
            "user": vendedor
        }
        crear_notificaciones_usuarios(users_list, context)
        
    for item_propuesta in lista_proximos:
        vendedor = item_propuesta.propuesta.negocio.vendedor
        comprador = item_propuesta.propuesta.negocio.comprador
        proveedor = item_propuesta.proveedor
        users_list = [vendedor, comprador, proveedor]
        context = {
            "titulo": f"Pago del artículo {item_propuesta.articulo} de {comprador.get_full_name()} {get_pago_estado(item_propuesta)}.",
            "categoria": "Vencimiento",
            "hyperlink": reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg}),
            "user": vendedor
        }
        crear_notificaciones_usuarios(users_list, context)
        

def notificate_entrega():
    negocios_cerrados_conf = Negocio.objects.filter(fecha_cierre__isnull=False).order_by('-timestamp')
        
    lista_atrasados = []
    lista_a_tiempo = []
    
    for negocio in negocios_cerrados_conf:
        
        try:
            propuesta = Propuesta.objects.filter(negocio=negocio).order_by('-timestamp').first()
        except Exception as e:
            print(e)
            
        item_propuestas_atrasados = get_atrasados_ayer_entrega(propuesta)
        item_propuestas_a_tiempo = get_a_tiempo_entrega(propuesta)
        
        lista_atrasados.extend(item_propuestas_atrasados)
        lista_a_tiempo.extend(item_propuestas_a_tiempo)
        
    for item_propuesta in lista_atrasados:
        comprador = item_propuesta.propuesta.negocio.comprador
        vendedor = item_propuesta.propuesta.negocio.vendedor
        proveedor = item_propuesta.proveedor
        users_list = [vendedor, comprador, proveedor]
        usuarios_logistica = MyUser.objects.filter(clase="Logistica", empresa=proveedor.empresa)
        users_list.extend(usuarios_logistica)
        context = {
            "titulo": f"La entrega del artículo {item_propuesta.articulo} de {comprador.get_full_name()} está atrasada ({item_propuesta.fecha_entrega_str})",
            "categoria": "Logistica",
            "proveedor": item_propuesta.proveedor,
            "hyperlink": reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg})
        }
        crear_notificaciones_usuarios(users_list, context)
        
    for item_propuesta in lista_a_tiempo:
        comprador = item_propuesta.propuesta.negocio.comprador
        vendedor = item_propuesta.propuesta.negocio.vendedor
        proveedor = item_propuesta.proveedor
        users_list = [vendedor, comprador, proveedor]
        usuarios_logistica = MyUser.objects.filter(clase="Logistica", empresa=proveedor.empresa)
        users_list.extend(usuarios_logistica)
        context = {
            "titulo": f"La entrega del artículo {item_propuesta.articulo} de {comprador.get_full_name()} está a tiempo (quedan {get_entrega_dias_restantes(item_propuesta)} dias).",
            "categoria": "Logistica",
            "proveedor": item_propuesta.proveedor,
            "hyperlink": reverse('negocio', kwargs={'id_de_neg': item_propuesta.propuesta.negocio.id_de_neg})
        }
        crear_notificaciones_usuarios(users_list, context)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        notificate_pago()
        notificate_entrega()