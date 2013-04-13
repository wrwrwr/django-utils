from django.contrib.sites.models import get_current_site


def site_context(site):
    return {
        'SITE_DOMAIN': site.domain,
        'SITE_NAME': site.name
    }


def site(request):
    current_site = get_current_site(request)
    context = site_context(current_site)
    context['BASE_URL'] = request.build_absolute_uri('/').rstrip('/')
    return context
