from django.http.response import HttpResponse
from django.urls import reverse
from social_django.utils import load_backend, load_strategy


def saml_metadata_view(request):
    complete_url = reverse('social:complete', args=("samldb", ))
    saml_backend = load_backend(
        load_strategy(request),
        "samldb",
        redirect_uri=complete_url,
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type='text/xml')
