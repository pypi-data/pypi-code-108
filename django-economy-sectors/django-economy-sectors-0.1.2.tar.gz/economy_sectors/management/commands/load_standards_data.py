from django.core.management.base import BaseCommand

from economy_sectors.models import EconomySector
from economy_sectors.utils import get_csv_reader_from_remote, bulk_create_update_from_csv

REMOTE_DIR = "https://package-files.s3.eu-central-1.amazonaws.com/django-economy-sectors/economy_sectors"

ECONOMY_SECTOR_FILES = [
    "nace_standard.csv",
    "ateco_standard.csv",
    "gics_standard.csv",
    "isic_standard.csv",
    "sic_standard.csv",
    "sae_standard.csv",
    "naics_standard.csv",
]


class Command(BaseCommand):
    help = 'Load economy sector data into the database'

    def handle(self, **options):
        print("Started...")

        for filename in ECONOMY_SECTOR_FILES:
            print(f"Processing {filename}...")
            print("Loading csv from remote...")
            reader = get_csv_reader_from_remote(f"{REMOTE_DIR}/{filename}")
            print("Preparing data to be created or updated...")
            bulk_create_update_from_csv(model=EconomySector, csv_reader=reader)
            print("Finished file.\n")

        print("Finished.")
