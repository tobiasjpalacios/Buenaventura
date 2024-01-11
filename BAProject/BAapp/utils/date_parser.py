from django.utils import timezone
from datetime import datetime

def date_parser(date: str):
    """
    date_parser toma como parametro una fecha string 
    y devuelve una fecha en formato timezone
    
    :param date_str: debe ser 'dd/mm/yyyy'
    :return: Devuelve la fecha formateada a timezone
    """
    fecha = datetime.strptime(date, '%d/%m/%Y')
    fecha_timezone = timezone.make_aware(fecha, timezone.get_current_timezone())
    return fecha_timezone