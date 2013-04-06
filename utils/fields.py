from django.db import models
from django.conf import settings

import forms


class URLField(models.URLField):
    """
    URLField that prepends some default schema and network location
    to schemaless paths. You may provide a base_url when creating the
    field (defaulting to "//current_site_domain/"), which will be
    adjoined to paths.
    """
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs.pop('base_url', None)
        super(URLField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.URLField,
            'base_url': self.base_url,
        }
        defaults.update(kwargs)
        return super(URLField, self).formfield(**defaults)


if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    rules = [((URLField,), [], {'base_url': ['base_url', {'default': None}]})]
    add_introspection_rules(rules, ['^utils\.fields\.'])
