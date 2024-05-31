# tu_aplicacion/templatetags/myfilters.py
from django import template
from datetime import datetime

register = template.Library()

@register.filter
def diferencia_dias(fecha1, fecha2):

    if isinstance(fecha1, str):
        fecha1 = datetime.strptime(fecha1, '%b %d, %Y')
    elif isinstance(fecha1, datetime):
        fecha1 = fecha1.date()
    
    if isinstance(fecha2, str):
        fecha2 = datetime.strptime(fecha2, '%b %d, %Y')
    elif isinstance(fecha2, datetime):
        fecha2 = fecha2.date()

    diferencia = (fecha2 - fecha1).days
    if diferencia >= 0:
        valor = diferencia
    else:
        valor = 0
    return valor
