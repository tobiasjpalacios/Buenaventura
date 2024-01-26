from BAapp.models import Negocio, Propuesta, ItemPropuesta
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import activate

def calcularVencAtr(a, b):
    if (a < b):
        return True
    return False   

def listasNA(negocioFilter, tipo):
    lista_negocios = []
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp','envio_comprador','visto')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            fecha_p = propuesta[0][1]
            envio = propuesta[0][2]
            visto = propuesta[0][3]
            valor_visto = "No"
            if (visto):
                valor_visto = "Si"
            if (envio == tipo):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop).values_list('articulo__ingrediente', flat=True)
                comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
                lista = {
                    'fecha':fecha_p,
                    'items':list(items),
                    'comprador': comprador,
                    'empresa':(negocio.comprador.empresa.razon_social),
                    'visto': valor_visto,
                    'id_de_neg': negocio.id_de_neg
                }
                lista_negocios.append(lista)
            else:
                pass
    return lista_negocios

def get_entrega_estado(item_propuesta):
    estado = None
    now = timezone.localtime(timezone.now()).date()
    
    try:
        if item_propuesta.fecha_entrega_date and item_propuesta.fecha_entrega_date < now:
            estado = "Atrasado"
        elif item_propuesta.fecha_entrega_date and item_propuesta.fecha_entrega_date >= now:
            estado = "A tiempo"
        else:
            raise ValueError(f"Propuesta {item_propuesta.propuesta.id}, {item_propuesta} no tiene fecha_entrega_date")
        
        if item_propuesta.fecha_salida_entrega and not item_propuesta.fecha_real_entrega:
            estado = "En Tránsito"
        elif item_propuesta.fecha_salida_entrega and item_propuesta.fecha_real_entrega:
            estado = "Entregado"
        elif not item_propuesta.fecha_salida_entrega and item_propuesta.fecha_real_entrega:
            raise ValueError(f"Propuesta {item_propuesta.propuesta.id}, {item_propuesta} no puede tener valor nulo en fecha_entrega_salida mientras fecha_real_entrega tenga valor")
        else:
            pass
    except ValueError as e:
        print(e)
        
    return estado

def create_item_propuesta_dict(fecha_pago, item_propuesta, comprador, id_de_neg, razon_social, destino, estado):
    return {
        'fecha':fecha_pago,
        'item_propuesta': item_propuesta,
        'comprador': comprador,
        'id_de_neg': id_de_neg,
        'empresa': razon_social,
        'destino': destino,
        'estado': estado
    }
    
def create_lista_item_propuestas(item_propuestas, negocio):
    return [
        create_item_propuesta_dict(
            item_propuesta.fecha_pago_str,
            item_propuesta.articulo,
            negocio.comprador.get_full_name(),
            negocio.id_de_neg,
            negocio.comprador.empresa.razon_social,
            item_propuesta.destino,
            get_entrega_estado(item_propuesta)
        ) 
        for item_propuesta in item_propuestas
    ]

def listaNL(request, negocioFilter):
    lista_items = []
    
    for id in negocioFilter:
        negocio = Negocio.objects.get(id=id)
        
        try:
            propuesta = Propuesta.objects.filter(negocio=negocio).order_by('-timestamp').first()
        except Exception as e:
            print(e)
            
        item_propuestas = ItemPropuesta.objects.filter(propuesta=propuesta, proveedor__empresa=request.user.empresa)
            
        lista_items.extend(create_lista_item_propuestas(item_propuestas, negocio))
        
    return lista_items

def get_vencidos_ayer_pago(propuesta):
    now = timezone.localtime(timezone.now()).date()
    yesterday = now - timedelta(days=1)
    vencidos_ayer_pago = ItemPropuesta.objects.filter(propuesta=propuesta, fecha_real_pago__isnull=True, fecha_pago_date__lt=now, fecha_pago_date__gte=yesterday)
    return vencidos_ayer_pago

def get_vencidos_pago(propuesta):
    now = timezone.localtime(timezone.now()).date()
    vencidos_pago = ItemPropuesta.objects.filter(propuesta=propuesta, fecha_real_pago__isnull=True, fecha_pago_date__lt=now)
    return vencidos_pago

def get_proximos_vencer_pago(propuesta):
    now = timezone.localtime(timezone.now()).date()
    seven_days_later = now + timezone.timedelta(days=7)
    proximos_vencer_pago = ItemPropuesta.objects.filter(propuesta=propuesta, fecha_real_pago__isnull=True, fecha_pago_date__range=[now, seven_days_later])
    return proximos_vencer_pago

def get_futuros_pago(propuesta):
    now = timezone.localtime(timezone.now()).date()
    futuros_pago = ItemPropuesta.objects.filter(propuesta=propuesta, fecha_real_pago__isnull=True, fecha_pago_date__gt=now + timezone.timedelta(days=7))
    return futuros_pago

def semaforoVencimiento(negocioFilter):
    lista_vencidos = []
    lista_proximos = []
    lista_futuros = []
    
    for id in negocioFilter:
        negocio = Negocio.objects.get(id=id)
        
        try:
            propuesta = Propuesta.objects.filter(negocio=negocio).order_by('-timestamp').first()
        except Exception as e:
            print(e)
            
        item_propuestas_vencidos = get_vencidos_pago(propuesta)
        item_propuestas_proximos = get_proximos_vencer_pago(propuesta)
        item_propuestas_futuros = get_futuros_pago(propuesta)
        
        lista_vencidos.extend(create_lista_item_propuestas(item_propuestas_vencidos, negocio))
        lista_proximos.extend(create_lista_item_propuestas(item_propuestas_proximos, negocio))
        lista_futuros.extend(create_lista_item_propuestas(item_propuestas_futuros, negocio))
    
    return lista_vencidos, lista_proximos, lista_futuros