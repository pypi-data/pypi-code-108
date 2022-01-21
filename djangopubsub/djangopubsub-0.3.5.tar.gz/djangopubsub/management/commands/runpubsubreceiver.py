# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from redis.exceptions import ConnectionError

from djangopubsub.djangoPubSub import DjangoPubSub as PubSub
from djangopubsub.handler import Handler as HandlerManager

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)


class Command(BaseCommand):
    help = _(u'Running Receiver PubSub!')
    error = False

    def runReceiverPubSub(self):
        try:
            events_map = HandlerManager().get_events_mapping()
            pubsub = PubSub()
            pubsub.receive(events_map)

        except ConnectionError as e:
            logger.error(str(e))

        except Exception as e:
            self.error = True
            logger.error(str(e), exc_info=True)

    def handle(self, *args, **options):
        logging.info('''------------------------------ Running PubSub --------------------------------
                        This is gonna take a few minutes...''')
        while not self.error:
            self.runReceiverPubSub()

        logging.info('''------------------------------ Finnished --------------------------------''')
