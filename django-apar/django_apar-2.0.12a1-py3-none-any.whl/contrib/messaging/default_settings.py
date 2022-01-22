"""Default settings for django-notifs project."""

from django.conf import settings


NOTIFICATIONS_PAGINATE_BY = getattr(settings, 'NOTIFICATIONS_PAGINATE_BY', 15)

NOTIFICATIONS_USE_WEBSOCKET = getattr(
    settings, 'NOTIFICATIONS_USE_WEBSOCKET', False
)

NOTIFICATIONS_CHANNELS = getattr(settings, 'NOTIFICATIONS_CHANNELS', {})

if NOTIFICATIONS_USE_WEBSOCKET:
    NOTIFICATIONS_CHANNELS['websocket'] = 'aparnik.contrib.messaging.channels.BasicWebSocketChannel'
