# chat/routing.py
from django.urls import re_path

from data.consumers import StartConsumer

websocket_urlpatterns = [
    re_path(r'ws/test', StartConsumer.StartConsumer.as_asgi()), ]
