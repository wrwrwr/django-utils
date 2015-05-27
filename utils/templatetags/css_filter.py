import re

from django import template
from django.template.defaultfilters import stringfilter

ALPHA = '(?:1|(?:0(?:\.\d{1,3})?))'
PERCENT = '(?:\d{1,3}%)'
COLOR_HEX_3 = r'#[a-fA-F0-9]{3}'
COLOR_HEX_6 = r'#[a-fA-F0-9]{6}'
COLOR_RGB = r'rgb\(\d{1,3},\s?\d{1,3},\s?\d{1,3}\)'
COLOR_RGBA = r'rgba\(\d{{1,3}},\s?\d{{1,3}},\s?\d{{1,3}},\s?{}\)'.format(ALPHA)
COLOR_HSL = r'hsl\(\d{1,3},\s?\d{1,3}%,\s?\d{1,3}%\)'
COLOR_HSLA = r'hsla\(\d{{1,3}},\s?{0},\s?{0},\s?{1}\)'.format(PERCENT, ALPHA)
COLOR_NAME_BASE = r'aqua|black|blue|fuchsia|gray|grey|green|lime|maroon|' \
                  r'navy|olive|purple|red|silver|teal|white|yellow'
COLOR = re.compile(r'{}|{}|{}|{}|{}|{}|{}'.format(
    COLOR_HEX_3, COLOR_HEX_6, COLOR_RGB, COLOR_RGBA, COLOR_HSL, COLOR_HSLA,
    COLOR_NAME_BASE))


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
