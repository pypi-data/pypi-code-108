import logging

from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Enable the consumer for an existing collection"
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name, used when posting to our api.",
        )

    def handle(self, *args, **options):
        name = options["name"]

        num_rows = Collection.objects.filter(name=name).update(consumer_enabled=True)
        if num_rows > 0:
            self.stdout.write(f"Enabled consumer for collection '{name}'.")
        else:
            self.stderr.write(
                f"Did not enable consumer for collection '{name}'. The collection"
                f"probably does not exist."
            )
