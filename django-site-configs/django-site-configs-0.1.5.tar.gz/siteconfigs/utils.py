# Utility to make sure to get the correct site object to use
from django.contrib.sites.models import Site


def get_current_site(request):
    return getattr(request, "site", Site.objects.get_current())
