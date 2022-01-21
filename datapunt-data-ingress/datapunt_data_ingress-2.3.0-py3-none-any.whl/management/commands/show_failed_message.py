from django.core.management.base import BaseCommand

from ingress.models import Collection, FailedMessage


class ShowFailedMessagesError(Exception):
    pass


class Command(BaseCommand):
    help = "Shows all info for a failed record (default: most recent). Optionally an collection name can specified."

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            nargs="?",
            default=None,
            help="The collection name",
        )
        parser.add_argument(
            "--ordering",
            default='desc',
            help="The ordering by which the failed messages should be searched. .",
        )

    def handle(self, *args, **options):
        name = options["name"]
        ordering = '-'
        if options['ordering'].lower() == 'asc':
            ordering = ''

        if name:
            try:
                collection = Collection.objects.get(name=name)
            except Collection.DoesNotExist:
                raise ShowFailedMessagesError(
                    f"\n\nThe collection with name '{name}' does not exist. Nothing has been done.\n\n"
                )

            failed_ingresses = FailedMessage.objects.filter(
                collection=collection
            ).order_by(f"{ordering}created_at")
        else:
            failed_ingresses = FailedMessage.objects.order_by("-created_at")

        if failed_ingresses.count() == 0:
            raise ShowFailedMessagesError(
                "No failed messages were found, nothing to show."
            )

        table_spacing = "{:<20} {:<50}"

        queue_attrs = (
            "created_at",
            "consume_started_at",
            "consume_succeeded_at",
            "consume_failed_at",
            "consume_fail_info",
            "raw_data",
        )

        failed_message = failed_ingresses.first()
        self.stdout.write(
            "\n\n" + table_spacing.format("collection", failed_message.collection.name)
        )
        for attr in queue_attrs:
            self.stdout.write(
                table_spacing.format(attr, str(getattr(failed_message, attr)) or "None")
            )
