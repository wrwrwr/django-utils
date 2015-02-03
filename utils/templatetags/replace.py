import re

from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.assignment_tag
def replace(pattern, replacement, value):
    """
    Performs a regex substitution on the value, the arguments
    order is the same as for ``re.sub``.

    Example:

        {% replace "regex" "replacement" string as new_string %}
        ...
        {{ new_string }}

    Replacement is realized using tags as filters are not meant to support
    multiple arguments; see: https://code.djangoproject.com/ticket/1199.
    """
    return re.sub(pattern, replacement, value)
