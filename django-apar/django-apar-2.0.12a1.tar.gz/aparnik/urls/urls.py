from django.conf.urls import url, include
from aparnik.views import install, share

app_name='aparnik'

urlpatterns = [
    url(r'^install$', install, name='install'),
    url(r'^share/', share, name='share'),
    url(r'^shops/', include('aparnik.packages.shops.urls.urls', namespace='shops')),
    url(r'^bank-gateways/', include('aparnik.packages.bankgateways.urls.urls', namespace='bank_gateways')),
]
