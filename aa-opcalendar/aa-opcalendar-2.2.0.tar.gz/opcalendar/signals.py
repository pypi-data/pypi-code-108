from .app_settings import (
    OPCALENDAR_NOTIFY_IMPORTS,
)

from django.dispatch import receiver

from django.db.models.signals import post_save, pre_delete
from .models import Event, IngameEvents
import datetime
from django.utils import timezone

from esi.clients import EsiClientProvider

from .app_settings import get_site_url

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

RED = 16711710
BLUE = 42751
GREEN = 6684416

esi = EsiClientProvider()


@receiver(post_save, sender=Event)
@receiver(post_save, sender=IngameEvents)
def fleet_saved(sender, instance, created, **kwargs):

    # Ingame Calendar Event
    if sender == IngameEvents and OPCALENDAR_NOTIFY_IMPORTS:
        try:
            logger.debug(
                "New signal created for New Ingame Calendar Event: %s" % instance.title
            )

            url = get_site_url() + "/opcalendar/ingame/event/{}/details/".format(
                instance.pk
            )

            message = "New ingame calendar event: %s" % instance.title

            # Get the entity name from owner name
            entity_id = esi.client.Search.get_search(
                categories=[instance.owner_type],
                search=instance.owner_name,
                strict=True,
            ).results()[instance.owner_type][0]

            logger.debug("Entity data is %s" % entity_id)

            main_char = instance.owner.character.character.character_name

            formup_system = instance.owner_name

            title = instance.title

            eve_time = instance.event_start_date

            fc = instance.owner_name

            # Setup portrait URL based on owner type
            if instance.owner_type == "alliance":

                portrait = "https://images.evetech.net/alliances/%s/logo" % entity_id

                ticker = "[{}]".format(
                    esi.client.Alliance.get_alliances_alliance_id(
                        alliance_id=entity_id
                    ).results()["ticker"]
                )

            if instance.owner_type == "corporation":

                portrait = "https://images.evetech.net/corporations/%s/logo" % entity_id

                ticker = "[{}]".format(
                    esi.client.Corporation.get_corporations_corporation_id(
                        corporation_id=entity_id
                    ).results()["ticker"]
                )

            if instance.owner_type == "character":

                portrait = (
                    "https://images.evetech.net/characters/%s/portrait" % entity_id
                )

                ticker = ""

            logger.debug("Portrait url is %s" % portrait)

            character_name = instance.owner_name

            # If we update instead of delete
            if not created:
                message = "Ingame calendar event updated: %s" % instance.title
                col = BLUE
            else:
                col = GREEN

            embed = {
                "title": message,
                "description": ("%s" % instance.text),
                "url": url,
                "color": col,
                "fields": [
                    {"name": "Owner", "value": fc, "inline": True},
                    {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                ],
                "footer": {
                    "icon_url": portrait,
                    "text": "{}  {}".format(character_name, ticker),
                },
            }

            hook = instance.owner.event_visibility

            old = datetime.datetime.now(timezone.utc) > eve_time

            if hook.webhook:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_fleets:
                        logger.debug("Event is in the past, not sending webhook.")
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

    # For Normal Events
    if sender == Event:
        # For normal events only
        if not instance.external:
            try:
                logger.debug("New signal fleet created for %s" % instance.title)

                url = get_site_url() + "/opcalendar/event/%s/details/" % instance.pk

                title = instance.title

                message = "New event: %s" % title

                main_char = instance.eve_character

                formup_system = instance.formup_system

                eve_time = instance.start_time

                fc = instance.fc

                portrait = main_char.portrait_url_64

                character_name = main_char.character_name

                ticker = "[{}]".format(main_char.corporation_ticker)

                # If we update instead of delete
                if not created:
                    message = "Updated Event: {}".format(title)
                    col = BLUE
                else:
                    col = GREEN

                embed = {
                    "title": message,
                    "description": ("%s" % instance.description),
                    "url": url,
                    "color": col,
                    "fields": [
                        {"name": "FC", "value": fc, "inline": True},
                        {
                            "name": "Type",
                            "value": instance.operation_type.name,
                            "inline": True,
                        },
                        {"name": "Formup", "value": formup_system, "inline": True},
                        {
                            "name": "Eve Time",
                            "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "inline": False,
                        },
                    ],
                    "footer": {
                        "icon_url": portrait,
                        "text": " %s %s, %s" % (character_name, ticker, instance.host),
                    },
                }
                hook = instance.event_visibility

                old = datetime.datetime.now(timezone.utc) > eve_time

                if hook.webhook:
                    if hook.webhook.enabled:
                        if old and hook.ignore_past_fleets:
                            logger.debug("Event is in the past, not sending webhook.")
                        hook.webhook.send_embed(embed)

            except Exception as e:
                logger.error(e)
                pass  # shits fucked... Don't worry about it...

        # For automated fleets like NPSI imported fleets. Only post if OPCALENDAR_NOTIFY_IMPORTS set to True
        if instance.external and OPCALENDAR_NOTIFY_IMPORTS:
            try:
                logger.debug("New signal fleet created for %s" % instance.title)

                url = get_site_url() + "/opcalendar/event/%s/details/" % instance.pk

                title = instance.title

                message = "New NPSI event from API: %s" % title

                main_char = instance.eve_character

                formup_system = instance.formup_system

                eve_time = instance.start_time

                fc = instance.fc

                portrait = main_char.portrait_url_64

                character_name = main_char.character_name

                ticker = "[{}]".format(main_char.corporation_ticker)

                # If we update instead of delete
                if not created:
                    message = "Updated Event: {}".format(title)
                    col = BLUE
                else:
                    col = GREEN

                embed = {
                    "title": message,
                    "description": ("%s" % instance.description),
                    "url": url,
                    "color": col,
                    "fields": [
                        {"name": "Community", "value": fc, "inline": True},
                        {
                            "name": "Type",
                            "value": instance.operation_type.name,
                            "inline": True,
                        },
                        {
                            "name": "Eve Time",
                            "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "inline": False,
                        },
                    ],
                    "footer": {
                        "icon_url": instance.host.logo_url,
                        "text": " %s" % instance.host,
                    },
                }

                hook = instance.event_visibility

                old = datetime.datetime.now(timezone.utc) > eve_time

                if hook.webhook:
                    if hook.webhook.enabled:
                        if old and hook.ignore_past_fleets:
                            logger.debug("Event is in the past, not sending webhook.")
                        hook.webhook.send_embed(embed)

            except Exception as e:
                logger.error(e)
                pass  # shits fucked... Don't worry about it...


@receiver(pre_delete, sender=Event)
@receiver(pre_delete, sender=IngameEvents)
def fleet_deleted(sender, instance, **kwargs):

    # Ingame Calendar Event
    if sender == IngameEvents and OPCALENDAR_NOTIFY_IMPORTS:
        try:
            logger.debug(
                "New signal created for Deleted Ingame Calendar Event: %s"
                % instance.title
            )

            url = get_site_url() + "/opcalendar/ingame/event/{}/details/".format(
                instance.pk
            )

            message = "Ingame calendar event deleted: %s" % instance.title

            # Get the entity name from owner name
            entity_id = esi.client.Search.get_search(
                categories=[instance.owner_type],
                search=instance.owner_name,
                strict=True,
            ).results()[instance.owner_type][0]

            logger.debug("Entity data is %s" % entity_id)

            main_char = instance.owner.character.character.character_name

            formup_system = instance.owner_name

            title = instance.title

            eve_time = instance.event_start_date

            fc = instance.owner_name

            col = RED

            # Setup portrait URL based on owner type
            if instance.owner_type == "alliance":

                portrait = "https://images.evetech.net/alliances/%s/logo" % entity_id

                ticker = "[{}]".format(
                    esi.client.Alliance.get_alliances_alliance_id(
                        alliance_id=entity_id
                    ).results()["ticker"]
                )

            if instance.owner_type == "corporation":

                portrait = "https://images.evetech.net/corporations/%s/logo" % entity_id

                ticker = "[{}]".format(
                    esi.client.Corporation.get_corporations_corporation_id(
                        corporation_id=entity_id
                    ).results()["ticker"]
                )

            if instance.owner_type == "character":

                portrait = (
                    "https://images.evetech.net/characters/%s/portrait" % entity_id
                )

                ticker = ""

            logger.debug("Portrait url is %s" % portrait)

            character_name = instance.owner_name

            embed = {
                "title": message,
                "description": ("%s" % instance.text),
                "url": url,
                "color": col,
                "fields": [
                    {"name": "Owner", "value": fc, "inline": True},
                    {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                ],
                "footer": {
                    "icon_url": portrait,
                    "text": "{}  {}".format(character_name, ticker),
                },
            }

            hook = instance.owner.event_visibility

            old = datetime.datetime.now(timezone.utc) > eve_time

            if hook.webhook:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_fleets:
                        logger.debug("Event is in the past, not sending webhook.")
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

    # For Normal Events
    if sender == Event:
        # For normal events only
        if not instance.external:
            try:
                logger.debug("New signal fleet created for %s" % instance.title)

                url = get_site_url() + "/opcalendar/event/%s/details/" % instance.pk

                title = instance.title

                message = "Event deleted: %s" % title

                main_char = instance.eve_character

                formup_system = instance.formup_system

                eve_time = instance.start_time

                fc = instance.fc

                portrait = main_char.portrait_url_64

                character_name = main_char.character_name

                ticker = "[{}]".format(main_char.corporation_ticker)

                col = RED

                embed = {
                    "title": message,
                    "description": ("%s" % instance.description),
                    "url": url,
                    "color": col,
                    "fields": [
                        {"name": "FC", "value": fc, "inline": True},
                        {
                            "name": "Type",
                            "value": instance.operation_type.name,
                            "inline": True,
                        },
                        {"name": "Formup", "value": formup_system, "inline": True},
                        {
                            "name": "Eve Time",
                            "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "inline": False,
                        },
                    ],
                    "footer": {
                        "icon_url": portrait,
                        "text": " %s %s, %s" % (character_name, ticker, instance.host),
                    },
                }

                hook = instance.event_visibility

                old = datetime.datetime.now(timezone.utc) > eve_time

                if hook.webhook:
                    if hook.webhook.enabled:
                        if old and hook.ignore_past_fleets:
                            logger.debug("Event is in the past, not sending webhook.")
                        hook.webhook.send_embed(embed)

            except Exception as e:
                logger.error(e)
                pass  # shits fucked... Don't worry about it...

        # For automated fleets like NPSI imported fleets. Only post if OPCALENDAR_NOTIFY_IMPORTS set to True
        if instance.external and OPCALENDAR_NOTIFY_IMPORTS:
            try:
                logger.debug("New signal fleet created for %s" % instance.title)

                url = get_site_url() + "/opcalendar/event/%s/details/" % instance.pk

                title = instance.title

                message = "NPSI event deleted from API: %s" % title

                main_char = instance.eve_character

                formup_system = instance.formup_system

                eve_time = instance.start_time

                fc = instance.fc

                portrait = main_char.portrait_url_64

                character_name = main_char.character_name

                ticker = "[{}]".format(main_char.corporation_ticker)

                col = RED

                embed = {
                    "title": message,
                    "description": ("%s" % instance.description),
                    "url": url,
                    "color": col,
                    "fields": [
                        {"name": "Community", "value": fc, "inline": True},
                        {
                            "name": "Eve Time",
                            "value": eve_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "inline": True,
                        },
                    ],
                    "footer": {
                        "icon_url": instance.host.logo_url,
                        "text": " %s" % instance.host,
                    },
                }

                hook = instance.event_visibility

                old = datetime.datetime.now(timezone.utc) > eve_time

                if hook.webhook:
                    if hook.webhook.enabled:
                        if old and hook.ignore_past_fleets:
                            logger.debug("Event is in the past, not sending webhook.")
                        hook.webhook.send_embed(embed)

            except Exception as e:
                logger.error(e)
                pass  # shits fucked... Don't worry about it...
