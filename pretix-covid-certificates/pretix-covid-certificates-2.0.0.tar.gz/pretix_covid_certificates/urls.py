from django.conf.urls import url

from pretix_covid_certificates.views import CovidCertificatesSettings

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/covidcerts/$",
        CovidCertificatesSettings.as_view(),
        name="settings",
    ),
]
