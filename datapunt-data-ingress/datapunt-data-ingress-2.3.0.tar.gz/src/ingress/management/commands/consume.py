import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from ingress.models import Collection
from ingress.settings import app_settings


class Command(BaseCommand):
    help = "Consume messages in the queue for a specific collection"
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "collection_name",
            help="The collection name for which to consume the messages from the queue",
        )

    def handle(self, *args, **options):
        collection_name = options["collection_name"]

        try:
            collection = Collection.objects.get(name=collection_name)
            consumer_class = app_settings.get_consumer_for_collection(collection.name)
        except Collection.DoesNotExist:
            self.stderr.write(f"The Collection '{collection_name}' does not exist.")
        except ObjectDoesNotExist as e:
            # Consumer does not exist in INGRESS_CONSUMER_CLASSES
            self.stderr.write(str(e))
        else:
            self.stdout.write(f"Starting consumer for '{collection_name}'")
            consumer = consumer_class()
            consumer.consume()
