import logging

from django.conf import settings
from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from isc_common.ws.webSocket import WebSocket

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        parser.add_argument('--message', type=str)

    def handle(self, *args, **options):
        username = options.get('username')
        user = User.objects.get(username=username)
        message = options.get('message')

        WebSocket.send_info_message(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{user.username}',
            message=message,
            logger=logger
        )
