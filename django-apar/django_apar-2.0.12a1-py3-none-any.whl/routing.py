from django.conf.urls import url

from aparnik.contrib.messaging.consumers import MessagingConsumer

app_name = 'aparnik'

websocket_urlpatterns = [
    url(r'^messaging/', MessagingConsumer),
]
