from urlparse import urljoin

from django import forms


class URLField(forms.URLField):
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs.pop('base_url', None)
        super(URLField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return value
        base_url = self.base_url
        if base_url is None:
            from django.contrib.sites.models import Site
            domain = Site.objects.get_current().domain
            base_url = '//{}/'.format(domain)
        value = urljoin(base_url, value)
        return super(URLField, self).to_python(value)
