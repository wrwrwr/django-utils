import re

from django import template
from django.template.defaultfilters import stringfilter


INPUT_START_WS = re.compile(r'\A\s+')
LINE_START_WS = re.compile(r'^(?!\n)\s*', re.MULTILINE)
LINE_START = re.compile(r'^(?!\n)', re.MULTILINE)


register = template.Library()


@register.filter
@stringfilter
def indent_filter(value, tabs=1):
    """
    Add some tabs before the value.
    """
    return LINE_START.sub(r'\t' * int(tabs), value)


@register.tag
def indent_tag(parser, token):
    """
    Makes each line in a block begin with a fixed amount of tabs and removes
    all whitespace at the block start.

    Example: 
        {% indent =2 %} fixes indentation (for each line removes all whitespace
                        from its start, and then prepends 2 tabs);
        {% indent +2 %} adds 2 tabs to each line;
        {% indent =2s %} does not remove starting whitespace (useful if you
                         don't want to indent your {% indent %} tags).
    """
    ns = parser.parse(('endindent',))
    parser.delete_first_token()
    ts = token.contents.split()
    if len(ts) > 1:
        a = ts[1]
        if a[0] in ('=', '+', '-',):
            m = a[0]
            a = a[1:]
        else:
            m = '+'
        if a[-1] == 's':
            s = False
            a = a[:-1]
        else:
            s = True
        i = int(a)
    else:
        m = '='
        i = 2
    return IndentNode(ns, m, i, s)


class IndentNode(template.Node):
    def __init__(self, nodes, mode, indent, starting):
        self.nodes = nodes
        self.mode = mode
        self.indent = indent
        self.starting = starting

    def render(self, context):
        r = self.nodes.render(context)
        i = r'\t' * int(self.indent)
        if self.mode == '=':
            r = LINE_START_WS.sub(i, r)
        elif self.mode == '+':
            r = LINE_START.sub(i, r)
        else:
             raise NotImplementedError(
                "Only fixed and plus are supported at the moment.")
        if self.starting:
            r = INPUT_START_WS.sub('', r)
        return r
