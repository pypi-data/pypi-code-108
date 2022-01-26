from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mocca_screening.import_mocca_register import import_mocca_register


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--csvfile",
            default=settings.MOCCA_REGISTER_FILE,
            dest="csvfile",
            help="Specify csv path and name",
        )

        parser.add_argument(
            "--force-delete",
            default=False,
            action="store_true",
            dest="force_delete",
            help="Force delete existing records. Cannot be undone!",
        )

    help = "Import MOCCA register (original)"

    def handle(self, *args, **options):
        try:
            import_mocca_register(
                path=options["csvfile"], force_delete=options["force_delete"]
            )
        except FileNotFoundError as e:
            raise CommandError(f"File not found. Got {e}")
