from django.core.management.base import BaseCommand
from django.db import transaction

from ingress.models import Collection, FailedMessage


class Command(BaseCommand):
    help = (
        "Moves all failed messages for the specified collection "
        "back to the main ingress queue to be parsed again."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "collection_name",
            help=(
                "The name of the collection. Use the 'list_collections' "
                "command to show the existing collections.",
            ),
        )

    def handle(self, *args, **options):
        collection_name = options["collection_name"]

        try:
            collection = Collection.objects.get(name=collection_name)
        except Collection.DoesNotExist:
            self.stderr.write(f"Collection named '{collection_name}' does not exist")
            return

        with transaction.atomic():
            failed_queryset = FailedMessage.objects.for_collection(collection)
            num_failed_messages = failed_queryset.count()
            start_message = (
                f"Start moving {num_failed_messages} from the failed queue "
                f"to the normal queue to be parsed again."
            )
            self.stdout.write(start_message)

            for failed_message in failed_queryset:
                failed_message.move_to_ingress_queue()

        end_message = (
            f"\n\nMoved {num_failed_messages} messages from the failed queue to "
            f"the normal queue to be parsed again.\n\n"
        )
        self.stdout.write(end_message)
