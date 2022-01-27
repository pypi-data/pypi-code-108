from django.core.management.base import BaseCommand
from django.db import connection, transaction

from osmflex.models import Osm


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):
        parser.add_argument("--truncate", action="store_true", help="Truncate current table data")

    def handle(self, *args, **options):
        @transaction.atomic()
        def __do():
            with connection.cursor() as c:
                for query in Osm.update_all_from_flex(truncate=options["truncate"]):
                    if options["verbosity"] > 0:
                        self.stdout.write(self.style.SUCCESS("Importing:"))
                        self.stdout.write(self.style.SUCCESS(query.as_string(c.cursor)))
                    try:
                        c.execute(query)
                    except:  # noqa: E722
                        self.stdout.write(self.style.ERROR("Failed to run SQL"))
                        raise

        __do()
