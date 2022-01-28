import logging

from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    event = settings.EVENT_STACK.EVENTS_TEST

    def add_arguments(self, parser):
        # parser.add_argument('--mode', type=str)
        # parser.add_argument('--qty', type=int)
        ...

    def handle(self, *args, **options):
        self.event.send_message('Hello World')
        print('Done.')
