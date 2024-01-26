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

def get_date(date):
    now = timezone.localtime(timezone.now()).date()
    m_date = date
    try:
        m_date = date_parser(date).date()
    except Exception:
        pass
    return now, m_date

def is_today(date):
    now, m_date = get_date(date)
    return now == m_date

def is_before_today(date):
    now, m_date = get_date(date)
    return now > m_date

def is_after_today(date):
    now, m_date = get_date(date)
    return now < m_date

def is_before(date_1, date_2):
    return date_1 < date_2