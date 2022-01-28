import logging
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from social_layer.tasks import format_medias

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Task that format the media files used by mediaultils app'

    def add_arguments(self, parser):
        parser.add_argument('--daemon', action='store_true')
        parser.add_argument('--interval', type=int, default=40)

    def handle(self, *args, **kwargs):
        """ Run the format media task. The options are:
        --daemon - this means that the it will run forever.
        --interval - sets the amount of sleep time between loops, if
                    'daemon' mode is set.
        """
        logger.info("Task format_media... Running.")
        while True:
            format_medias()
            if not kwargs.get('daemon'):
                break
            sleep(kwargs.get('interval'))


