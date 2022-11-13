from django import template

register = template.Library()

@register.simple_tag
def multiply(a, b) -> float:
    return float(a) * float(b)