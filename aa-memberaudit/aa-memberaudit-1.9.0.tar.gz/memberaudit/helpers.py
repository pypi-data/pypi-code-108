from typing import Optional

from django.db import models
from django.utils.html import format_html
from eveuniverse.models import EveSolarSystem

from allianceauth.eveonline.evelinks import dotlan
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from app_utils.views import link_html

from . import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def get_or_create_esi_or_none(
    prop_name: str, dct: dict, Model: type
) -> Optional[models.Model]:
    """Gets or creates a new eveuniverse object from a dictionary entry.

    return the object on success or None
    """
    if dct.get(prop_name):
        obj, _ = Model.objects.get_or_create_esi(id=dct.get(prop_name))
    else:
        obj = None

    return obj


def get_or_create_or_none(
    prop_name: str, dct: dict, Model: type
) -> Optional[models.Model]:
    """Get or creates a Django object from a dictionary entry or returns None."""
    if dct.get(prop_name):
        obj, _ = Model.objects.get_or_create(id=dct.get(prop_name))
        return obj
    return None


def get_or_none(prop_name: str, dct: dict, Model: type) -> Optional[models.Model]:
    """Gets a new Django object from a dictionary entry
    or returns None if it does not exist."""
    id = dct.get(prop_name)
    if id:
        try:
            return Model.objects.get(id=id)
        except Model.DoesNotExist:
            pass
    return None


def eve_solar_system_to_html(solar_system: EveSolarSystem, show_region=True) -> str:
    if solar_system.is_high_sec:
        css_class = "text-high-sec"
    elif solar_system.is_low_sec:
        css_class = "text-low-sec"
    else:
        css_class = "text-null-sec"

    region_html = (
        f" / {solar_system.eve_constellation.eve_region.name}" if show_region else ""
    )
    return format_html(
        '{} <span class="{}">{}</span>{}',
        link_html(dotlan.solar_system_url(solar_system.name), solar_system.name),
        css_class,
        round(solar_system.security_status, 1),
        region_html,
    )
