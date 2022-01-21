from django.conf.urls import url
from django.urls import include, path

from .views import saml_metadata_view

urlpatterns = [
    path('saml/metadata/', saml_metadata_view),
    url('', include('social_django.urls', namespace='social')),
]
