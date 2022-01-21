import logging

from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Disable the consumer for an existing collection"
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name, used when posting to our api.",
        )

    def handle(self, *args, **options):
        name = options["name"]

        num_rows = Collection.objects.filter(name=name).update(consumer_enabled=False)
        if num_rows > 0:
            self.stdout.write(f"Disabled consumer for collection '{name}'.")
        else:
            self.stderr.write(
                f"Did not disable consumer for collection '{name}'. The collection"
                f"probably does not exist."
            )
