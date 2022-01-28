from django.urls import path

from isc_common.ws.consumer import Consumer

websocket_urlpatterns = [
    path('ws/<channel>/', Consumer),
]
