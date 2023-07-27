from django import template

register = template.Library()

@register.simple_tag
def formatfloat(value):
    if not value:
        return "Sin definir"
    
    if value.is_integer():
        return str(int(value))
    else:
        return "{:.2f}".format(value)