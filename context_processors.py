from django.contrib.sites.models import get_current_site


def site(request):
    current_site = get_current_site(request)
    return {
        'BASE_URL': request.build_absolute_uri('/'),
        'SITE_DOMAIN': current_site.domain,
        'SITE_NAME': current_site.name
    }
