from django import template

register = template.Library()

@register.simple_tag
def decimaltofloat(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None