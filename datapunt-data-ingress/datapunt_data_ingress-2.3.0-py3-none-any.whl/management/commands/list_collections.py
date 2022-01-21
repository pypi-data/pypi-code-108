from django.core.management.base import BaseCommand

from ingress.models import Collection


class Command(BaseCommand):
    help = "List all existing collections"

    def handle(self, *args, **options):
        collections = Collection.objects.order_by("id")

        self.stdout.write(f"\nCurrent number of collections: {collections.count()}\n")
        if collections.count() == 0:
            return

        table_spacing = "{:<4} {:<25} {:<15} {:<16} {:<10} {:<10} {:<30}"
        header = table_spacing.format(
            "id",
            "name",
            "ingress_enabled",
            "consumer_enabled",
            "unparsed",
            "failed",
            "full url",
        )
        self.stdout.write(header)
        for c in collections:
            self.stdout.write(
                table_spacing.format(
                    c.id,
                    c.name,
                    "yes" if c.ingress_enabled else "no",
                    "yes" if c.consumer_enabled else "no",
                    c.message_set.filter(consume_started_at__isnull=True).count(),
                    c.failedmessage_set.count(),
                    c.url_path or "None",
                )
            )
