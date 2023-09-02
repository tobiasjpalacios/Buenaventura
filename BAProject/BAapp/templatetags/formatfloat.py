from django import template

register = template.Library()

@register.simple_tag
def formatfloat(value, is_precio):
    """
    Pasar False en is_precio cuando se quiera renderizar en el value
    de un campo de texto así is_precio fuere True.
    """
    if not value:
        return "Sin definir"
    
    if value.is_integer():
        new_value = str(int(value))
    else:
        new_value = "{:.2f}".format(value)

    result = f"$ {new_value} USD" if is_precio else new_value

    return result

@register.simple_tag
def formatprecioforinput(value):
    if value.is_integer():
        new_integer = int(value)
        new_value = str(new_integer) + "00"
    else:
        new_format = "{:.2f}".format(value)
        new_str = str(new_format).split('.')
        new_value = ''.join(new_str)

    result = new_value + '0'

    return result