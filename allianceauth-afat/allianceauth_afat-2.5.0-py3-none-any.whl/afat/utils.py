"""
Utilities
"""

# Standard Library
from typing import Optional

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import lazy
from django.utils.html import format_html

# Alliance Auth
from allianceauth.authentication.admin import User
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.providers import esi

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

# Format for output of datetime for this app
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

format_html_lazy = lazy(format_html, str)


class NoDataError(Exception):
    """
    NoDataError
    """

    def __init__(self, msg):
        Exception.__init__(self, msg)


def write_log(request: WSGIRequest, log_event: str, fatlink_hash: str, log_text: str):
    """
    Write the log
    :param request:
    :type request:
    :param log_event:
    :type log_event:
    :param fatlink_hash:
    :type fatlink_hash:
    :param log_text:
    :type log_text:
    :return:
    :rtype:
    """

    # Alliance Auth AFAT
    from afat.models import AFatLog

    afat_log = AFatLog()
    afat_log.user = request.user
    afat_log.log_event = log_event
    afat_log.log_text = log_text
    afat_log.fatlink_hash = fatlink_hash
    afat_log.save()


def get_or_create_character(
    name: str = None, character_id: int = None
) -> Optional[EveCharacter]:
    """
    This function takes a name or id of a character and checks
    to see if the character already exists.
    If the character does not already exist, it will create the
    character object, and if needed the corp/alliance objects as well.
    :param name:
    :type name:
    :param character_id:
    :type character_id:
    :return:
    :rtype:
    """

    eve_character = None

    if name:
        # If a name is passed to this function, we have to check it on ESI
        result = esi.client.Search.get_search(
            categories=["character"], search=name, strict=True
        ).result()

        if "character" not in result:
            return None

        character_id = result["character"][0]
        eve_character = EveCharacter.objects.filter(character_id=character_id)
    elif character_id:
        # If an ID is passed to this function, we can just check the db for it.
        eve_character = EveCharacter.objects.filter(character_id=character_id)
    elif not name and not character_id:
        raise NoDataError("No character name or character id provided.")

    if eve_character is not None and len(eve_character) == 0:
        # Create character
        character = EveCharacter.objects.create_character(character_id)
        character = EveCharacter.objects.get(pk=character.pk)

        logger.info(f"EveCharacter Object created: {character.character_name}")

        # Create alliance and corporation info objects if not already exists for
        # future sanity
        if character.alliance_id is not None:
            # Create alliance and corporation info objects if not already exists
            if not EveAllianceInfo.objects.filter(
                alliance_id=character.alliance_id
            ).exists():
                EveAllianceInfo.objects.create_alliance(character.alliance_id)
        else:
            # Create corporation info object if not already exists
            if not EveCorporationInfo.objects.filter(
                corporation_id=character.corporation_id
            ).exists():
                EveCorporationInfo.objects.create_corporation(character.corporation_id)
    else:
        character = eve_character[0]

    return character


def get_or_create_corporation_info(corporation_id: int) -> EveCorporationInfo:
    """
    Get or create corporation info
    :param corporation_id:
    :type corporation_id:
    :return:
    :rtype:
    """

    try:
        eve_corporation_info = EveCorporationInfo.objects.get(
            corporation_id=corporation_id
        )
    except EveCorporationInfo.DoesNotExist:
        eve_corporation_info = EveCorporationInfo.objects.create_corporation(
            corp_id=corporation_id
        )

        logger.info(
            f"EveCorporationInfo Object created: {eve_corporation_info.corporation_name}"
        )

    return eve_corporation_info


def get_or_create_alliance_info(alliance_id: int) -> EveAllianceInfo:
    """
    Get or create alliance info
    :param alliance_id:
    :type alliance_id:
    :return:
    :rtype:
    """

    try:
        eve_alliance_info = EveAllianceInfo.objects.get(alliance_id=alliance_id)
    except EveAllianceInfo.DoesNotExist:
        eve_alliance_info = EveAllianceInfo.objects.create_alliance(
            alliance_id=alliance_id
        )

        logger.info(
            f"EveAllianceInfo Object created: {eve_alliance_info.alliance_name}"
        )

    return eve_alliance_info


def get_main_character_from_user(user: User) -> str:
    """
    Get the main character from a user
    :param user:
    :type user:
    :return:
    :rtype:
    """

    user_main_character = user.username

    try:
        user_profile = user.profile
        user_main_character = user_profile.main_character.character_name
    except AttributeError:
        pass

    return user_main_character
