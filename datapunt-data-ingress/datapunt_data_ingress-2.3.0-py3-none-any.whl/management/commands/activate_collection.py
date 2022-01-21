import logging

from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Activate an existing collection"
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name, used when posting to our api.",
        )

    def handle(self, *args, **options):
        name = options["name"]

        num_rows = Collection.objects.filter(name=name).update(ingress_enabled=True)
        if num_rows > 0:
            self.stdout.write(
                f"Activated Collection '{name}', it will now accept ingress"
            )
        else:
            self.stderr.write(
                f"Did not activate Collection '{name}'. It probably does not exist."
            )
