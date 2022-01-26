"""
views helper
"""

# Standard Library
import random

# Django
from django.contrib.auth.models import Permission
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission

# Alliance Auth AFAT
from afat.models import AFat, AFatLink, AFatLog, AFatLogEvent
from afat.utils import get_main_character_from_user


def convert_fatlinks_to_dict(
    request: WSGIRequest, fatlink: AFatLink, close_esi_redirect: str = None
) -> dict:
    """
    Converts an AFatLink object into a dictionary
    :param request:
    :type request:
    :param fatlink:
    :type fatlink:
    :param close_esi_redirect:
    :type close_esi_redirect:
    :return:
    :rtype:
    """

    # Fleet name
    fatlink_fleet = fatlink.fleet if fatlink.fleet is not None else fatlink.hash

    # ESI marker
    via_esi = "No"
    esi_fleet_marker = ""

    # Check for ESI link
    if fatlink.is_esilink:
        via_esi = "Yes"
        esi_fleet_marker_classes = "label label-default afat-label afat-label-via-esi"

        if fatlink.is_registered_on_esi:
            esi_fleet_marker_classes += " afat-label-active-esi-fleet"

        marker_text = _("via ESI")
        esi_fleet_marker += (
            f'<span class="{esi_fleet_marker_classes}">{marker_text}</span>'
        )

    # Fleet type
    fatlink_type = fatlink.link_type.name if fatlink.link_type else ""

    # Creator name
    creator_main_character = get_main_character_from_user(user=fatlink.creator)

    # Fleet time
    fleet_time = fatlink.afattime
    fleet_time_timestamp = fleet_time.timestamp()

    # Action buttons
    actions = ""
    if (
        fatlink.is_esilink
        and fatlink.is_registered_on_esi
        and fatlink.creator == request.user
    ):
        button_close_esi_tracking_url = reverse(
            "afat:fatlinks_close_esi_fatlink", args=[fatlink.hash]
        )

        close_esi_redirect_parameter = (
            f"?next={close_esi_redirect}" if close_esi_redirect is not None else ""
        )

        button_title = _(
            "Clicking here will stop the automatic tracking through ESI for this fleet and close the associated FAT link."
        )
        modal_body_text = _(
            f"<p>Are you sure you want to close ESI fleet with ID {fatlink.esi_fleet_id} from {fatlink.character.character_name}?</p>"
        )
        modal_confirm_text = _("Stop Tracking")

        actions += (
            '<a class="btn btn-afat-action btn-primary btn-sm" '
            f'style="margin-left: 0.25rem;" title="{button_title}" data-toggle="modal" '
            'data-target="#cancelEsiFleetModal" '
            f'data-url="{button_close_esi_tracking_url}{close_esi_redirect_parameter}" '
            f'data-body-text="{modal_body_text}" '
            f'data-confirm-text="{modal_confirm_text}">'
            '<i class="fas fa-times"></i></a>'
        )

    if request.user.has_perm("afat.manage_afat") or request.user.has_perm(
        "afat.add_fatlink"
    ):
        button_edit_url = reverse("afat:fatlinks_details_fatlink", args=[fatlink.hash])

        actions += (
            '<a class="btn btn-afat-action btn-info btn-sm" '
            f'href="{button_edit_url}"><span class="fas fa-eye"></span></a>'
        )

    if request.user.has_perm("afat.manage_afat"):
        button_delete_url = reverse("afat:fatlinks_delete_fatlink", args=[fatlink.hash])
        button_delete_text = _("Delete")
        modal_body_text = _(
            f"<p>Are you sure you want to delete FAT link {fatlink_fleet}?</p>"
        )

        actions += (
            '<a class="btn btn-afat-action btn-danger btn-sm" data-toggle="modal" '
            f'data-target="#deleteFatLinkModal" data-url="{button_delete_url}" '
            f'data-confirm-text="{button_delete_text}"'
            f'data-body-text="{modal_body_text}">'
            '<span class="glyphicon glyphicon-trash">'
            "</span></a>"
        )

    summary = {
        "pk": fatlink.pk,
        "fleet_name": fatlink_fleet + esi_fleet_marker,
        "creator_name": creator_main_character,
        "fleet_type": fatlink_type,
        "fleet_time": {"time": fleet_time, "timestamp": fleet_time_timestamp},
        "fats_number": fatlink.afats_count,
        "hash": fatlink.hash,
        "is_esilink": fatlink.is_esilink,
        "esi_fleet_id": fatlink.esi_fleet_id,
        "is_registered_on_esi": fatlink.is_registered_on_esi,
        "actions": actions,
        "via_esi": via_esi,
    }

    return summary


def convert_fats_to_dict(request: WSGIRequest, fat: AFat) -> dict:
    """
    Converts an AFat object into a dictionary
    :param request:
    :type request:
    :param fat:
    :type fat:
    :return:
    :rtype:
    """

    # fleet type
    fleet_type = (
        fat.afatlink.link_type.name if fat.afatlink.link_type is not None else ""
    )

    # esi marker
    via_esi = "No"
    esi_fleet_marker = ""

    if fat.afatlink.is_esilink:
        via_esi = "Yes"
        esi_fleet_marker_classes = "label label-default afat-label afat-label-via-esi"

        if fat.afatlink.is_registered_on_esi:
            esi_fleet_marker_classes += " afat-label-active-esi-fleet"

        marker_text = _("via ESI")
        esi_fleet_marker += (
            f'<span class="{esi_fleet_marker_classes}">{marker_text}</span>'
        )

    # actions
    actions = ""
    if request.user.has_perm("afat.manage_afat"):
        button_delete_fat = reverse(
            "afat:fatlinks_delete_fat", args=[fat.afatlink.hash, fat.id]
        )
        button_delete_text = _("Delete")
        modal_body_text = _(
            f"<p>Are you sure you want to remove {fat.character.character_name} from this FAT link?</p>"
        )

        actions += (
            '<a class="btn btn-danger btn-sm" '
            'data-toggle="modal" '
            'data-target="#deleteFatModal" '
            f'data-url="{button_delete_fat}" '
            f'data-confirm-text="{button_delete_text}"'
            f'data-body-text="{modal_body_text}">'
            '<span class="glyphicon glyphicon-trash"></span>'
            "</a>"
        )

    fleet_time = fat.afatlink.afattime
    fleet_time_timestamp = fleet_time.timestamp()
    fleet_name = (
        fat.afatlink.fleet if fat.afatlink.fleet is not None else fat.afatlink.hash
    )

    summary = {
        "system": fat.system,
        "ship_type": fat.shiptype,
        "character_name": fat.character.character_name,
        "fleet_name": fleet_name + esi_fleet_marker,
        "fleet_time": {"time": fleet_time, "timestamp": fleet_time_timestamp},
        "fleet_type": fleet_type,
        "via_esi": via_esi,
        "actions": actions,
    }

    return summary


def convert_logs_to_dict(log: AFatLog, fatlink_exists: bool = False) -> dict:
    """
    Convert AFatLog to dict
    :param log:
    :type log:
    :param fatlink_exists:
    :type fatlink_exists:
    :return:
    :rtype:
    """

    log_time = log.log_time
    log_time_timestamp = log_time.timestamp()

    # User name
    user_main_character = get_main_character_from_user(user=log.user)

    fatlink_html = _(f"{log.fatlink_hash} (Deleted)")
    if fatlink_exists is True:
        fatlink_link = reverse("afat:fatlinks_details_fatlink", args=[log.fatlink_hash])
        fatlink_html = f'<a href="{fatlink_link}">{log.fatlink_hash}</a>'

    fatlink = {"html": fatlink_html, "hash": log.fatlink_hash}

    summary = {
        "log_time": {"time": log_time, "timestamp": log_time_timestamp},
        "log_event": AFatLogEvent(log.log_event).label,
        "user": user_main_character,
        "fatlink": fatlink,
        "description": log.log_text,
    }

    return summary


def get_random_rgba_color():
    """
    Get a random RGB(a) color
    :return:
    :rtype:
    """

    return "rgba({red}, {green}, {blue}, 1)".format(
        red=random.randint(0, 255),
        green=random.randint(0, 255),
        blue=random.randint(0, 255),
    )


def characters_with_permission(permission: Permission) -> models.QuerySet:
    """
    Returns queryset of characters that have the given permission
    in Auth through due to their associated user
    :param permission:
    :type permission:
    :return:
    :rtype:
    """

    # First we need the users that have the permission
    users_qs = users_with_permission(permission)

    # Now get their characters ...
    charater_qs = EveCharacter.objects.filter(character_ownership__user__in=users_qs)

    return charater_qs
