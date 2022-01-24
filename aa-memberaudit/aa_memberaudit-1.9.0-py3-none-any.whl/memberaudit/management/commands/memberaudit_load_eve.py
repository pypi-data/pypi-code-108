import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

from app_utils.logging import LoggerAddTag

from ... import __title__
from ...constants import (
    EVE_CATEGORY_ID_BLUEPRINT,
    EVE_CATEGORY_ID_CHARGE,
    EVE_CATEGORY_ID_DRONE,
    EVE_CATEGORY_ID_FIGHTER,
    EVE_CATEGORY_ID_IMPLANT,
    EVE_CATEGORY_ID_MODULE,
    EVE_CATEGORY_ID_SHIP,
    EVE_CATEGORY_ID_SKILL,
    EVE_CATEGORY_ID_STRUCTURE,
)

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "Preloads data required for this app from ESI"

    def handle(self, *args, **options):
        call_command(
            "eveuniverse_load_types",
            __title__,
            "--category_id",
            str(EVE_CATEGORY_ID_BLUEPRINT),
            "--category_id",
            str(EVE_CATEGORY_ID_SHIP),
            "--category_id",
            str(EVE_CATEGORY_ID_MODULE),
            "--category_id",
            str(EVE_CATEGORY_ID_CHARGE),
            "--category_id",
            str(EVE_CATEGORY_ID_SKILL),
            "--category_id",
            str(EVE_CATEGORY_ID_DRONE),
            "--category_id_with_dogma",
            str(EVE_CATEGORY_ID_IMPLANT),
            "--category_id",
            str(EVE_CATEGORY_ID_FIGHTER),
            "--category_id",
            str(EVE_CATEGORY_ID_STRUCTURE),
        )
