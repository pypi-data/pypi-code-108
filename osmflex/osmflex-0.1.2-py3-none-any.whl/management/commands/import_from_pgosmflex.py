from django.core.management.base import BaseCommand

from osmflex.models import Osm


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def handle(self, *args, **options):
        Osm.update_all_from_flex()
