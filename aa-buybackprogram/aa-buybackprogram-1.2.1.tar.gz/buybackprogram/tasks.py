import requests
from bravado.exception import HTTPBadGateway, HTTPGatewayTimeout, HTTPServiceUnavailable
from celery import shared_task

from django.db import Error
from django.utils import timezone
from eveuniverse.models import EveMarketPrice

from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

from buybackprogram.models import ItemPrices, Owner

from .app_settings import BUYBACKPROGRAM_TASKS_TIME_LIMIT

logger = get_extension_logger(__name__)

NORMAL_TASK_PRIORITY = 4

# Create your tasks here
TASK_DEFAULT_KWARGS = {
    "time_limit": BUYBACKPROGRAM_TASKS_TIME_LIMIT,
}

TASK_ESI_KWARGS = {
    **TASK_DEFAULT_KWARGS,
    **{
        "bind": True,
        "autoretry_for": (
            OSError,
            HTTPBadGateway,
            HTTPGatewayTimeout,
            HTTPServiceUnavailable,
        ),
        "retry_kwargs": {"max_retries": 3},
        "retry_backoff": 30,
    },
}


@shared_task
def update_all_prices():

    i = 0
    type_ids = []
    market_data = {}

    # Get all type ids
    prices = ItemPrices.objects.all()

    logger.debug("Price setup starting for %s items from Fuzzworks API" % len(prices))

    # Build suitable bulks to fetch prices from API
    for item in prices:
        type_ids.append(item.eve_type_id)

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
            market_data.update(items_fuzzwork)

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
    market_data.update(items_fuzzwork)

    logger.debug("Market data fetched, starting database update...")
    for price in prices:

        buy = int(float(market_data[str(price.eve_type_id)]["buy"]["max"]))
        sell = int(float(market_data[str(price.eve_type_id)]["sell"]["min"]))

        price.buy = buy
        price.sell = sell
        price.updated = timezone.now()

    try:
        ItemPrices.objects.bulk_update(prices, ["buy", "sell", "updated"])
        logger.debug("All prices succesfully updated")
    except Error as e:
        logger.error("Error updating prices: %s" % e)

    EveMarketPrice.objects.update_from_esi()

    logger.debug("Updated all eveuniverse market prices.")


@shared_task(
    **{
        **TASK_ESI_KWARGS,
        **{
            "base": QueueOnce,
            "once": {"keys": ["owner_pk"], "graceful": True},
            "max_retries": None,
        },
    }
)
def update_contracts_for_owner(self, owner_pk):
    """fetches all contracts for owner from ESI"""

    return _get_owner(owner_pk).update_contracts_esi()


@shared_task(**TASK_DEFAULT_KWARGS)
def update_all_contracts():
    logger.debug("Starting all contract updates")
    for owner in Owner.objects.all():
        logger.debug("Updating contracts for %s" % owner)
        update_contracts_for_owner.apply_async(
            kwargs={"owner_pk": owner.pk},
            priority=NORMAL_TASK_PRIORITY,
        )


def _get_owner(owner_pk: int) -> Owner:
    """returns the owner or raises exception"""
    try:
        owner = Owner.objects.get(pk=owner_pk)
    except Owner.DoesNotExist:
        raise Owner.DoesNotExist(
            "Requested owner with pk {} does not exist".format(owner_pk)
        )
    return owner
