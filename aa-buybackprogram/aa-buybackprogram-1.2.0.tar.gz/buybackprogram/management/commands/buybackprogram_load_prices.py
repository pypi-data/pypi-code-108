import requests

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone
from eveuniverse.models import EveType

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import ItemPrices

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = (
        "Preloads price data required for the buyback program from fuzzwork market API"
    )

    def handle(self, *args, **options):
        i = 0
        item_count = 0
        type_ids = []
        market_data = []

        # Get all type ids
        typeids = EveType.objects.values_list("id", flat=True).filter(published=True)

        print(
            "Price setup starting for %s items from Fuzzworks API, this may take up to 30 seconds..."
            % len(typeids)
        )

        # Build suitable bulks to fetch prices from API
        for item in typeids:
            type_ids.append(item)

            i += 1

            if i == 1000:

                response_fuzzwork = requests.get(
                    "https://market.fuzzwork.co.uk/aggregates/",
                    params={
                        "types": ",".join([str(x) for x in type_ids]),
                        "station": 60003760,
                    },
                )

                items_fuzzwork = response_fuzzwork.json()
                market_data.append(items_fuzzwork)

                i = 0
                type_ids.clear()

        # Get leftover data from the bulk
        response_fuzzwork = requests.get(
            "https://market.fuzzwork.co.uk/aggregates/",
            params={
                "types": ",".join([str(x) for x in type_ids]),
                "station": 60003760,
            },
        )

        items_fuzzwork = response_fuzzwork.json()
        market_data.append(items_fuzzwork)

        objs = []

        for objects in market_data:
            for key, value in objects.items():
                item_count += 1

                item = ItemPrices(
                    eve_type_id=key,
                    buy=int(float(value["buy"]["max"])),
                    sell=int(float(value["sell"]["min"])),
                    updated=timezone.now(),
                )

                objs.append(item)
        try:
            ItemPrices.objects.bulk_create(objs)
            return "Succesfully setup %s prices." % item_count
        except IntegrityError:
            print(
                "Error: Prices already loaded into database, did you mean to run task.update_all_prices instead?"
            )

            delete_arg = input("Would you like to delete current prices? (y/n): ")

            if delete_arg == "y":
                ItemPrices.objects.all().delete()
                return "All price data removed from database. Run the command again to populate the price data."
            else:
                return "No changes done to price table."


# from buybackprogram.tasks import update_all_prices
