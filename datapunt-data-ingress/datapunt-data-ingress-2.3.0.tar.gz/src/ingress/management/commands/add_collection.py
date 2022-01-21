from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "Adds a new collection"

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help=(
                "The collection name, used when posting to our api. "
                "For example: with the name being 'people_data_v2', the url will be "
                "'/ingress/people_data_v2' (with no slash at the end)."
            ),
        )

    def handle(self, *args, **options):
        name = options["name"]

        c = Collection(name=name)
        c.full_clean()
        c.save()
        self.stdout.write(
            f"Created Collection '{c.name}' (active: {c.ingress_enabled}, "
            f"consumer enabled: {c.consumer_enabled})"
        )
