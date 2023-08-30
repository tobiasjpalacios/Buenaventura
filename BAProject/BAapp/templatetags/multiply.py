from django import template
from .formatfloat import formatfloat

register = template.Library()

@register.simple_tag
def multiply(a, b) -> float:
    mult = float(a) * float(b)
    result = formatfloat(mult)
    return result