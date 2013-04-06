from django import template
from django.utils.formats import number_format


register = template.Library()


@register.filter
def percentage(value, precision=2):
    """
    Displays a fraction as a percentage.
    See: https://code.djangoproject.com/ticket/17662.
    """
    try:
        precision = int(precision)
        value = float(value) * 100
    except (TypeError, ValueError):
        return value
    value = round(value, precision)
    return number_format(value, decimal_pos=precision) + u'%'
