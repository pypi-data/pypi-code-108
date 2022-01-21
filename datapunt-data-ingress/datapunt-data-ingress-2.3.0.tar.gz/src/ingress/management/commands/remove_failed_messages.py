from django.core.management.base import BaseCommand

from ingress.models import Collection, FailedMessage


class Command(BaseCommand):
    help = "Remove all failed messages for an existing collection"

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name",
        )

    def handle(self, *args, **options):
        name = options["name"]

        collection = Collection.objects.filter(name=name).first()

        if not collection:
            self.stdout.write(f"Collection '{name}' does not exist")
            return

        num_deleted, _ = FailedMessage.objects.filter(collection=collection).delete()

        self.stdout.write(
            f"{num_deleted} failed messages removed for collection '{name}'"
        )
