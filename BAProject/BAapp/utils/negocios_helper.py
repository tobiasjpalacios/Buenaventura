from BAapp.models import Negocio, Propuesta, ItemPropuesta
from datetime import datetime
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

def listaNL(request,negocioFilter):
    lista_negocios = []
    en_tiempo = False
    en_transito = False
    entregado = False
    atrasado = False
    for a in negocioFilter:
        negocio = Negocio.objects.get(id=a)
        propuesta = list(Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').values_list('id','timestamp')[:1])
        if (not propuesta):
            pass
        else:
            id_prop = propuesta[0][0]
            comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre        
            modulo = request.user.clase
            #P = Proveedor 4
            if (modulo == 'Proveedor'):    
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, proveedor__id=request.user.id)
            #L = Logistica 6
            elif (modulo == 'Logistica'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=request.user.id)
            #A = Administrador 1
            elif (modulo == 'Administrador'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, empresa__id=request.user.id)
            #C = Comprador 2
            elif (modulo == 'Comprador'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop, propuesta__negocio__comprador__id=request.user.id)
            #V = Vendedor 3
            elif (modulo == 'Vendedor'):
                items = ItemPropuesta.objects.filter(propuesta__id = id_prop)
            else:
                items = []
            
            
            if (items.count() < 1):
                pass
            else:
                destino = ""
                estado = ""
                destino_tiempo = ""
                fecha_tiempo = "00/00/0000"
                destino_transito = ""
                fecha_transito = "00/00/0000"
                destino_entregado = ""
                fecha_entregado = "00/00/0000"
                destino_atrasado = ""
                fecha_atrasado = "00/00/0000"
                primero_tiempo = True
                primero_transito = True
                primero_entregado = True
                primero_atrasado = True
                today = datetime.today()
                for b in items:
                    fechaEntrega = datetime.strptime(b.fecha_entrega, "%d/%m/%Y")
                    resultado = calcularVencAtr(fechaEntrega, today)
                    print (resultado)
                    if (b.fecha_real_entrega is not None):
                        #Entregado
                        entregado = True
                        if (primero_entregado):
                            fecha_entregado = b.fecha_entrega
                            destino_entregado = b.destino
                            primero_entregado = False
                        else:
                            fechaEntregado = datetime.strptime(fecha_entregado, "%d/%m/%Y")
                            res = calcularVencAtr(b.fecha_entrega, fecha_entregado)
                            if (not res):
                                fecha_entregado = b.fecha_entrega
                                destino_entregado = b.destino
                    else:
                        if (not resultado):
                            if (b.fecha_salida_entrega is None):
                                #A Tiempo
                                en_tiempo = True
                                if (primero_tiempo):
                                    fecha_tiempo = b.fecha_entrega
                                    destino_tiempo = b.destino
                                    primero_tiempo = False
                                else:
                                    fechaTiempo = datetime.strptime(fecha_tiempo, "%d/%m/%Y")
                                    res = calcularVencAtr(fechaEntrega, fechaTiempo)
                                    if (not res):
                                        fecha_tiempo = b.fecha_entrega
                                        destino_tiempo = b.destino
                            else:
                                #En Transito
                                en_transito = True
                                if (primero_transito):
                                    fecha_transito = b.fecha_entrega
                                    destino_transito = b.destino
                                    primero_transito = False
                                else:
                                    res = calcularVencAtr(b.fecha_entrega, fecha_transito)
                                    if (not res):
                                        fecha_transito = b.fecha_entrega
                                        destino_transito = b.destino
                        else:
                            #Atrasado
                            atrasado = True
                            if (primero_atrasado):
                                    fecha_atrasado = b.fecha_entrega    
                                    destino_atrasado = b.destino
                                    primero_atrasado = False
                            else:
                                fechaAtrasado = datetime.strptime(fecha_atrasado, "%d/%m/%Y")
                                res = calcularVencAtr(b.fecha_entrega, fecha_atrasado)
                                if (not res):
                                    fecha_atrasado = b.fecha_entrega
                                    destino_atrasado = b.destino
                if (atrasado):
                    estado = "Atrasado"
                    destino = destino_atrasado
                    fecha = fecha_atrasado
                elif (en_tiempo):
                    estado = "A Tiempo"
                    destino = destino_tiempo
                    fecha = fecha_tiempo
                elif (en_transito):
                    estado = "En Tránsito"
                    destino = destino_transito
                    fecha = fecha_transito
                else:
                    estado = "Entregado"
                    destino = destino_entregado
                    fecha = fecha_entregado      
                lista = {
                    'fecha':fecha,
                    'destinatario': comprador,
                    'destino': destino,
                    'id_de_neg':negocio.id_de_neg,
                    'empresa':negocio.comprador.empresa.razon_social,
                    'estado':estado
                }
                lista_negocios.append(lista)
                en_tiempo = False
                en_transito = False
                entregado = False
                atrasado = False
    return lista_negocios

def get_articulos_vencidos(id_prop):
    now = timezone.localtime(timezone.now()).date()
    articulos_vencidos = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True, fecha_pago__lt=now)
    return articulos_vencidos

def get_articulos_proximos_a_vencer(id_prop):
    now = timezone.localtime(timezone.now()).date()
    seven_days_later = now + timezone.timedelta(days=7)
    articulos_proximos_a_vencer = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True, fecha_pago__range=[now, seven_days_later])
    return articulos_proximos_a_vencer

def get_articulos_futuros(id_prop):
    now = timezone.localtime(timezone.now()).date()
    articulos_futuros = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True, fecha_pago__gt=now + timezone.timedelta(days=7))
    return articulos_futuros

def create_articulo_dict(fecha_pago, comprador, id_de_neg, razon_social):
    return {
        'fecha':fecha_pago,
        'comprador': comprador,
        'id_de_neg': id_de_neg,
        'empresa': razon_social
    }
    
def create_lista_articulos(articulos, negocio):
    return [
        create_articulo_dict(
            articulo.fecha_pago,
            negocio.comprador.get_full_name(),
            negocio.id_de_neg,
            negocio.comprador.empresa.razon_social
        ) 
        for articulo in articulos
    ]

def semaforoVencimiento(negocioFilter):
    lista_vencidos = []
    lista_proximos = []
    lista_futuros = []
    
    for id in negocioFilter:
        negocio = Negocio.objects.get(id=id)
        
        try:
            propuesta = Propuesta.objects.filter(negocio__id = negocio.id).order_by('-timestamp').first()
        except Exception as e:
            print(e)
            
        articulos_vencidos = get_articulos_vencidos(propuesta.id)
        articulos_proximos = get_articulos_proximos_a_vencer(propuesta.id)
        articulos_futuros = get_articulos_futuros(propuesta.id)
        
        lista_vencidos.extend(create_lista_articulos(articulos_vencidos, negocio))
        lista_proximos.extend(create_lista_articulos(articulos_proximos, negocio))
        lista_futuros.extend(create_lista_articulos(articulos_futuros, negocio))
    
    return lista_vencidos, lista_proximos, lista_futuros
        # if (not propuesta):
        #     pass
        # else:
        #     id_prop = propuesta[0][0]
        #     fecha_p = propuesta[0][1]
        #     articulos_vencidos(id_prop)
        #     articulos_proximos_a_vencer(id_prop)
        #     articulos_futuros(id_prop)
            # items = ItemPropuesta.objects.filter(propuesta__id = id_prop, fecha_real_pago__isnull=True).values_list('articulo__ingrediente', 'fecha_pago')
            # if (items.count() > 0):
            #     comprador = negocio.comprador.apellido +" "+negocio.comprador.nombre
            #     id_propuesta = id_prop        
            #     vencidos = False
            #     esta_semana = False
            #     futuros = False
            #     for a in items:                    
            #         date_time_obj = datetime.strptime(a[1], "%d/%m/%Y")
            #         if (date_time_obj < today2):
            #             vencidos = True
            #         else:
            #             difDias = (today2 - date_time_obj).days                        
            #             if ((difDias * (-1)) <= 7):
            #                 esta_semana = True
            #             else:
            #                 futuros = True
            #         """
            #         diaP = int(a[1][0:2])
            #         mesP = int(a[1][3:5])
            #         añoP = int(a[1][6:10])
            #         difD = (diaP - diaA)
            #         difM = (mesP - mesA)
            #         difA = (añoP - añoA)
            #         proxMes = (diaP + 30 - diaA)
            #         if ((mesA == 12 and mesP == 1) and (difA == 1)):
            #             difM = 1
            #         if ((difA < 0) or (difM < 0 and difA == 0) or ((((diaP > diaA) and (mesP < mesA)) or ((diaP < diaA) and (mesP == mesA))))):
            #             vencidos = True 
            #         elif ((diaP==diaA) and (mesP==mesA) and (añoP==añoA)):
            #             esta_semana = True
            #         elif (((mesP == mesA) and (difD < 8 and difD > 0)) or ((difM == 1) and ((proxMes < 8 and proxMes > 0) and (diaP < 7)))):
            #             esta_semana = True
            #         else:
            #             futuros = True
            #         """
            #     if (vencidos):
            #         lista = {
            #             'fecha':fecha_p,
            #             'comprador': comprador,
            #             'id_de_neg': negocio.id_de_neg,
            #             'empresa':negocio.comprador.empresa.razon_social
            #         }
            #         lista_vencidos.append(lista)
            #     elif (esta_semana):
            #         lista = {
            #             'fecha':fecha_p,
            #             'comprador': comprador,
            #             'id_de_neg': negocio.id_de_neg,
            #             'empresa':negocio.comprador.empresa.razon_social
            #         }
            #         lista_semanas.append(lista)
            #     else:
            #         lista = {
            #             'fecha':fecha_p,
            #             'comprador': comprador,
            #             'id_de_neg': negocio.id_de_neg,
            #             'empresa':negocio.comprador.empresa.razon_social
            #         }
            #         lista_futuros.append(lista)
            #     vencidos = False
            #     esta_semana = False
            #     futuros = False