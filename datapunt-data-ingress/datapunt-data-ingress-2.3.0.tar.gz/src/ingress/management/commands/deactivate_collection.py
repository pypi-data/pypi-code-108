from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Deactivate an existing collection"

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The collection name, used when posting to our api.",
        )

    def handle(self, *args, **options):
        name = options["name"]

        num_rows = Collection.objects.filter(name=name).update(ingress_enabled=False)
        if num_rows > 0:
            self.stdout.write(
                f"Dectivated Collection '{name}', it will now longer accept ingress"
            )
        else:
            self.stderr.write(
                f"Did not deactivate Collection '{name}'. It probably does not exist."
            )
