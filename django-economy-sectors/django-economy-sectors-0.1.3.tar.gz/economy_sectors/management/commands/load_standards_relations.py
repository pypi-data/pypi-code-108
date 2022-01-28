from django.core.management.base import BaseCommand

from economy_sectors.models import EconomySectorRelation
from economy_sectors.utils import bulk_create_update_from_csv, get_csv_reader_from_remote

REMOTE_DIR = "https://package-files.s3.eu-central-1.amazonaws.com/django-economy-sectors/economy_sectors_relations"

ECONOMY_SECTOR_RELATIONS_FILES = [
    "nace_relations.csv",
    "ateco_relations.csv",
    "gics_relations.csv",
    "isic_relations.csv",
    "naics_relations.csv",
]


class Command(BaseCommand):
    help = 'Load relations between different economy sector into the database'

    def handle(self, **options):
        print("Started...")

        for filename in ECONOMY_SECTOR_RELATIONS_FILES:
            print(f"Processing {filename}...")
            print("Loading csv from remote...")
            reader = get_csv_reader_from_remote(f"{REMOTE_DIR}/{filename}")
            print("Preparing data to be created or updated...")
            bulk_create_update_from_csv(model=EconomySectorRelation, csv_reader=reader)
            print("Finished file.\n")

        print("Finished.")
