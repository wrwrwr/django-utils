import re

from django import template
from django.template.defaultfilters import stringfilter


COLOR_HEX_3 = r'#[a-fA-F0-9]{3}'
COLOR_HEX_6 = r'#[a-fA-F0-9]{6}'
COLOR_NAME_BASE = r'aqua|black|blue|fuchsia|gray|grey|green|lime|maroon|' \
                  r'navy|olive|purple|red|silver|teal|white|yellow'
COLOR = re.compile(r'{}|{}|{}'.format(COLOR_HEX_3, COLOR_HEX_6, COLOR_NAME_BASE))


register = template.Library()


@register.filter
@stringfilter
def escapecss(value, kind='color'):
    """
    Escape a CSS attribute value of some given kind.
    """
    if kind == 'color':
        if COLOR.match(value):
            return value
        else:
            return ''
    else:
        raise NotImplemented("Don't know how to escape this kind of value.")
