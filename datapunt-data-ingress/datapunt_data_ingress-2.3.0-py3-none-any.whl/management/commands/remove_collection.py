from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Remove an existing collection"

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name, used when posting to our api.",
        )

    def handle(self, *args, **options):
        name = options["name"]

        num_deleted, _ = Collection.objects.filter(name=name).delete()
        if num_deleted > 0:
            self.stdout.write(f"Deleted Collection '{name}'")
        else:
            self.stderr.write(
                f"Did not delete Collection '{name}'. It probably does not exist."
            )
