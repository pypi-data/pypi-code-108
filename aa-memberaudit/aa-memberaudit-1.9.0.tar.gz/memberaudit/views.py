import datetime as dt
from typing import Optional, Tuple

import humanize

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Count, F, Max, Q, Sum
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timeuntil
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy
from esi.decorators import token_required
from eveuniverse.core import eveimageserver
from eveuniverse.models import EveType

from allianceauth.authentication.models import CharacterOwnership, get_guest_state_pk
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from app_utils.messages import messages_plus
from app_utils.views import (
    bootstrap_icon_plus_name_html,
    bootstrap_label_html,
    fontawesome_link_button_html,
    link_html,
    no_wrap_html,
    yesno_str,
    yesnonone_str,
)

from . import __title__, tasks
from .app_settings import MEMBERAUDIT_APP_NAME, MEMBERAUDIT_DATA_EXPORT_MIN_UPDATE_AGE
from .constants import EVE_CATEGORY_ID_SHIP
from .core import data_exporters
from .decorators import fetch_character_if_allowed
from .helpers import eve_solar_system_to_html
from .models import (
    Character,
    CharacterAsset,
    CharacterContract,
    CharacterContractItem,
    CharacterMail,
    General,
    Location,
    SkillSet,
    SkillSetGroup,
    SkillSetSkill,
)

# module constants
MY_DATETIME_FORMAT = "Y-M-d H:i"
DATETIME_FORMAT = "%Y-%b-%d %H:%M"
MAIL_LABEL_ID_ALL_MAILS = 0
MAP_SKILL_LEVEL_ARABIC_TO_ROMAN = {0: "-", 1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
UNGROUPED_SKILL_SET = gettext_lazy("[Ungrouped]")
DEFAULT_ICON_SIZE = 32
ICON_SIZE_64 = 64
CHARACTER_VIEWER_DEFAULT_TAB = "mails"
SKILL_SET_DEFAULT_ICON_TYPE_ID = 3327
ICON_FAILED = "fas fa-times boolean-icon-false"
ICON_PARTIAL = "fas fa-check text-warning"
ICON_FULL = "fas fa-check-double text-success"
ICON_MET_ALL_REQUIRED = "fas fa-check text-success"

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def item_icon_plus_name_html(item, size=DEFAULT_ICON_SIZE) -> Tuple[str, str]:
    """returns generated HTML with name and icon for asset and contract items"""
    if item.is_blueprint_copy:
        variant = item.eve_type.IconVariant.BPC
    else:
        variant = None

    name = item.name_display
    name_html = bootstrap_icon_plus_name_html(
        icon_url=item.eve_type.icon_url(size=DEFAULT_ICON_SIZE, variant=variant),
        name=name,
        size=size,
    )
    return name_html, name


def create_main_organization_html(main_character) -> str:
    return format_html(
        "{}{}",
        main_character.corporation_name,
        f" [{main_character.alliance_ticker}]" if main_character.alliance_name else "",
    )


def add_common_context(request, context: dict) -> dict:
    """adds the common context used by all view"""
    unregistered_count = Character.objects.unregistered_characters_of_user_count(
        request.user
    )
    new_context = {
        **{
            "app_title": MEMBERAUDIT_APP_NAME,
            "unregistered_count": unregistered_count,
            "MY_DATETIME_FORMAT": MY_DATETIME_FORMAT,
        },
        **context,
    }
    return new_context


@login_required
@permission_required("memberaudit.basic_access")
def index(request):
    return redirect("memberaudit:launcher")


#############################
# Section: Characters


@login_required
@permission_required("memberaudit.basic_access")
def launcher(request) -> HttpResponse:
    owned_chars_query = (
        CharacterOwnership.objects.filter(user=request.user)
        .select_related(
            "character",
            "memberaudit_character",
            "memberaudit_character__wallet_balance",
            "memberaudit_character__skillpoints",
            "memberaudit_character__unread_mail_count",
        )
        .order_by()
    )
    has_auth_characters = owned_chars_query.count() > 0
    auth_characters = list()
    unregistered_chars = list()
    for character_ownership in owned_chars_query:
        eve_character = character_ownership.character
        try:
            character = character_ownership.memberaudit_character
        except AttributeError:
            unregistered_chars.append(eve_character.character_name)
        else:
            auth_characters.append(
                {
                    "character_id": eve_character.character_id,
                    "character_name": eve_character.character_name,
                    "character": character,
                    "alliance_id": eve_character.alliance_id,
                    "alliance_name": eve_character.alliance_name,
                    "corporation_id": eve_character.corporation_id,
                    "corporation_name": eve_character.corporation_name,
                }
            )

    unregistered_chars = sorted(unregistered_chars)

    try:
        main_character_id = request.user.profile.main_character.character_id
    except AttributeError:
        main_character_id = None

    context = {
        "page_title": "My Characters",
        "auth_characters": auth_characters,
        "has_auth_characters": has_auth_characters,
        "unregistered_chars": unregistered_chars,
        "has_registered_characters": len(auth_characters) > 0,
        "main_character_id": main_character_id,
    }

    """
    if has_auth_characters:
        messages_plus.warning(
            request,
            format_html(
                "Please register all your characters. "
                "You currently have <strong>{}</strong> unregistered characters.",
                unregistered_chars,
            ),
        )
    """
    return render(
        request,
        "memberaudit/launcher.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.basic_access")
@token_required(scopes=Character.get_esi_scopes())
def add_character(request, token) -> HttpResponse:
    token_char = EveCharacter.objects.get(character_id=token.character_id)
    try:
        character_ownership = CharacterOwnership.objects.select_related(
            "character"
        ).get(user=request.user, character=token_char)
    except CharacterOwnership.DoesNotExist:
        messages_plus.error(
            request,
            format_html(
                "You can register your main or alt characters."
                "However, character <strong>{}</strong> is neither. ",
                token_char.character_name,
            ),
        )
    else:
        with transaction.atomic():
            character, _ = Character.objects.update_or_create(
                character_ownership=character_ownership
            )

        tasks.update_character.delay(character_pk=character.pk)
        messages_plus.success(
            request,
            format_html(
                "<strong>{}</strong> has been registered. "
                "Note that it can take a minute until all character data is visible.",
                character.character_ownership.character,
            ),
        )

    return redirect("memberaudit:launcher")


@login_required
@permission_required("memberaudit.basic_access")
def remove_character(request, character_pk: int) -> HttpResponse:
    try:
        character = Character.objects.select_related(
            "character_ownership__user", "character_ownership__character"
        ).get(pk=character_pk)
    except Character.DoesNotExist:
        return HttpResponseNotFound(f"Character with pk {character_pk} not found")

    character_name = character.character_ownership.character.character_name
    if character.character_ownership.user == request.user:
        character.delete()
        messages_plus.success(
            request,
            format_html(
                "Removed character <strong>{}</strong> as requested.", character_name
            ),
        )
    else:
        return HttpResponseForbidden(
            f"No permission to remove Character with pk {character_pk}"
        )

    return redirect("memberaudit:launcher")


@login_required
@permission_required(["memberaudit.basic_access", "memberaudit.share_characters"])
def share_character(request, character_pk: int) -> HttpResponse:
    try:
        character = Character.objects.select_related(
            "character_ownership__user", "character_ownership__character"
        ).get(pk=character_pk)
    except Character.DoesNotExist:
        return HttpResponseNotFound(f"Character with pk {character_pk} not found")

    if character.character_ownership.user == request.user:
        character.is_shared = True
        character.save()
    else:
        return HttpResponseForbidden(
            f"No permission to remove Character with pk {character_pk}"
        )

    return redirect("memberaudit:launcher")


@login_required
@permission_required("memberaudit.basic_access")
def unshare_character(request, character_pk: int) -> HttpResponse:
    try:
        character = Character.objects.select_related(
            "character_ownership__user", "character_ownership__character"
        ).get(pk=character_pk)
    except Character.DoesNotExist:
        return HttpResponseNotFound(f"Character with pk {character_pk} not found")

    if character.character_ownership.user == request.user:
        character.is_shared = False
        character.save()
    else:
        return HttpResponseForbidden(
            f"No permission to remove Character with pk {character_pk}"
        )

    return redirect("memberaudit:launcher")


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed(
    "details",
    "wallet_balance",
    "skillpoints",
    "character_ownership__user",
    "character_ownership__user__profile__main_character",
    "character_ownership__character",
    "location__location",
    "location__eve_solar_system",
    "location__eve_solar_system__eve_constellation__eve_region",
    "online_status",
)
def character_viewer(request, character_pk: int, character: Character) -> HttpResponse:
    """main view for showing a character with all details

    Args:
    - character_pk: PK for character to be shown

    GET Params:
    - tab: ID of tab to be shown  (optional)
    """
    # character details
    try:
        character_details = character.details
    except ObjectDoesNotExist:
        character_details = None

    # main character
    auth_character = character.character_ownership.character
    try:
        main_character = character.character_ownership.user.profile.main_character
        main = f"[{main_character.corporation_ticker}] {main_character.character_name}"
    except AttributeError:
        main_character = None
        main = "-"

    # mailing lists
    mailing_lists_qs = character.mailing_lists.all().annotate(
        unread_count=Count("recipient_mails", filter=Q(recipient_mails__is_read=False))
    )
    mailing_lists = [
        {
            "list_id": obj.id,
            "name_plus": obj.name_plus,
            "unread_count": obj.unread_count,
        }
        for obj in mailing_lists_qs
    ]

    # mail labels
    mail_labels = list(
        character.mail_labels.values(
            "label_id", "name", unread_count_2=F("unread_count")
        )
    )
    total_unread_count = sum(
        [obj["unread_count_2"] for obj in mail_labels if obj["unread_count_2"]]
    )
    total_unread_count += sum(
        [obj["unread_count"] for obj in mailing_lists if obj["unread_count"]]
    )
    mail_labels.append(
        {
            "label_id": MAIL_LABEL_ID_ALL_MAILS,
            "name": "All Mails",
            "unread_count_2": total_unread_count,
        }
    )

    # list of all characters owned by this user for sidebar
    accessible_characters = set(
        Character.objects.user_has_access(user=request.user).values_list(
            "pk", flat=True
        )
    )
    all_characters = (
        EveCharacter.objects.select_related(
            "character_ownership__memberaudit_character"
        )
        .filter(character_ownership__user=character.character_ownership.user)
        .order_by("character_name")
        .annotate(
            memberaudit_character_pk=F("character_ownership__memberaudit_character")
        )
        .annotate(is_shared=F("character_ownership__memberaudit_character__is_shared"))
        .values(
            "character_id", "character_name", "memberaudit_character_pk", "is_shared"
        )
    )
    all_characters = [
        {
            **obj,
            **{
                "has_access": (obj["memberaudit_character_pk"] in accessible_characters)
            },
        }
        for obj in all_characters
    ]

    # assets total value
    character_assets_total = (
        character.assets.exclude(is_blueprint_copy=True)
        .aggregate(
            total=Sum(
                F("quantity") * F("eve_type__market_price__average_price"),
                output_field=models.FloatField(),
            )
        )
        .get("total")
    )

    # implants
    try:
        has_implants = character.implants.count() > 0
    except ObjectDoesNotExist:
        has_implants = False

    # last updates
    try:
        last_updates = {
            obj["section"]: obj["finished_at"]
            for obj in character.update_status_set.filter(is_success=True).values(
                "section", "finished_at"
            )
        }
    except ObjectDoesNotExist:
        last_updates = None

    page_title = "Character Sheet"
    if not character.user_is_owner(request.user):
        page_title = format_html(
            '{}&nbsp;<i class="far fa-eye" title="You do not own this character"></i>',
            page_title,
        )

    context = {
        "page_title": page_title,
        "character": character,
        "auth_character": auth_character,
        "character_details": character_details,
        "mail_labels": mail_labels,
        "mailing_lists": mailing_lists,
        "main": main,
        "main_character_id": main_character.character_id if main_character else None,
        "all_characters": all_characters,
        "show_tab": request.GET.get("tab", ""),
        "last_updates": last_updates,
        "character_assets_total": character_assets_total,
        "has_implants": has_implants,
        "is_assets_updating": character.is_section_updating(
            Character.UpdateSection.ASSETS
        ),
    }
    return render(
        request,
        "memberaudit/character_viewer.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_assets_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        asset_qs = (
            character.assets.annotate_pricing()
            .select_related(
                "eve_type",
                "eve_type__eve_group",
                "eve_type__eve_group__eve_category",
                "location__eve_solar_system",
                "location__eve_solar_system__eve_constellation__eve_region",
            )
            .filter(location__isnull=False)
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    assets_with_children_ids = set(
        character.assets.filter(children__isnull=False).values_list(
            "item_id", flat=True
        )
    )
    location_counts = {
        obj["id"]: obj["items_count"]
        for obj in (
            Location.objects.select_related("characterasset__character")
            .filter(characterasset__character=character)
            .annotate(items_count=Count("characterasset"))
            .values("id", "items_count")
        )
    }
    for asset in asset_qs:
        if asset.location.eve_solar_system:
            region = asset.location.eve_solar_system.eve_constellation.eve_region.name
            solar_system = asset.location.eve_solar_system.name
        else:
            region = ""
            solar_system = ""

        is_ship = yesno_str(
            asset.eve_type.eve_group.eve_category_id == EVE_CATEGORY_ID_SHIP
        )

        if asset.item_id in assets_with_children_ids:
            ajax_children_url = reverse(
                "memberaudit:character_asset_container",
                args=[character.pk, asset.pk],
            )
            actions_html = (
                '<button type="button" class="btn btn-default btn-sm" '
                'data-toggle="modal" data-target="#modalCharacterAssetContainer" '
                f"data-ajax_children_url={ajax_children_url}>"
                '<i class="fas fa-search"></i></button>'
            )
        else:
            actions_html = ""

        location_name = (
            f"{asset.location.name_plus} ({location_counts.get(asset.location_id, 0)})"
        )
        name_html, name = item_icon_plus_name_html(asset)
        data.append(
            {
                "item_id": asset.item_id,
                "location": location_name,
                "name": {"display": name_html, "sort": name},
                "quantity": asset.quantity if not asset.is_singleton else "",
                "group": asset.group_display,
                "volume": asset.eve_type.volume,
                "price": asset.price,
                "total": asset.total,
                "actions": actions_html,
                "region": region,
                "solar_system": solar_system,
                "is_ship": is_ship,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_asset_container(
    request, character_pk: int, character: Character, parent_asset_pk: int
) -> HttpResponse:
    try:
        parent_asset = character.assets.select_related(
            "location", "eve_type", "eve_type__eve_group"
        ).get(pk=parent_asset_pk)
    except CharacterAsset.DoesNotExist:
        error_msg = (
            f"Asset with pk {parent_asset_pk} not found for character {character}"
        )
        logger.warning(error_msg)
        context = {
            "error": error_msg,
        }
    else:
        context = {
            "character": character,
            "parent_asset": parent_asset,
            "parent_asset_icon_url": parent_asset.eve_type.icon_url(
                size=DEFAULT_ICON_SIZE
            ),
        }
    return render(
        request,
        "memberaudit/modals/character_viewer/asset_container_content.html",
        context,
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_asset_container_data(
    request, character_pk: int, character: Character, parent_asset_pk: int
) -> JsonResponse:
    data = list()
    try:
        parent_asset = character.assets.get(pk=parent_asset_pk)
    except CharacterAsset.DoesNotExist:
        error_msg = (
            f"Asset with pk {parent_asset_pk} not found for character {character}"
        )
        logger.warning(error_msg)
        return HttpResponseNotFound(error_msg)

    try:
        assets_qs = parent_asset.children.annotate_pricing().select_related(
            "eve_type",
            "eve_type__eve_group",
            "eve_type__eve_group__eve_category",
        )
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    for asset in assets_qs:
        name_html, name = item_icon_plus_name_html(asset)
        data.append(
            {
                "item_id": asset.item_id,
                "name": {"display": name_html, "sort": name},
                "quantity": asset.quantity if not asset.is_singleton else "",
                "group": asset.group_display,
                "volume": asset.eve_type.volume,
                "price": asset.price,
                "total": asset.total,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_contacts_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        for contact in character.contacts.select_related("eve_entity").all():
            is_watched = contact.is_watched is True
            is_blocked = contact.is_blocked is True
            name = contact.eve_entity.name
            is_npc = contact.eve_entity.is_npc
            if is_npc:
                name_plus = format_html(
                    "{} {}", name, bootstrap_label_html("NPC", "info")
                )
            else:
                name_plus = name

            name_html = bootstrap_icon_plus_name_html(
                contact.eve_entity.icon_url(DEFAULT_ICON_SIZE), name_plus, avatar=True
            )
            data.append(
                {
                    "id": contact.eve_entity_id,
                    "name": {"display": name_html, "sort": name},
                    "standing": contact.standing,
                    "type": contact.eve_entity.get_category_display().title(),
                    "is_watched": is_watched,
                    "is_blocked": is_blocked,
                    "is_watched_str": yesno_str(is_watched),
                    "is_blocked_str": yesno_str(is_blocked),
                    "is_npc_str": yesno_str(is_npc),
                    "level": contact.standing_level.title(),
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_contracts_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        for contract in character.contracts.select_related("issuer", "assignee").all():
            if now() < contract.date_expired:
                time_left = timeuntil(contract.date_expired, now())
            else:
                time_left = "expired"

            ajax_contract_detail = reverse(
                "memberaudit:character_contract_details",
                args=[character.pk, contract.pk],
            )

            actions_html = (
                '<button type="button" class="btn btn-primary" '
                'data-toggle="modal" data-target="#modalCharacterContract" '
                f"data-ajax_contract_detail={ajax_contract_detail}>"
                '<i class="fas fa-search"></i></button>'
            )
            data.append(
                {
                    "contract_id": contract.contract_id,
                    "summary": contract.summary(),
                    "type": contract.get_contract_type_display().title(),
                    "from": contract.issuer.name,
                    "to": contract.assignee.name if contract.assignee else "(None)",
                    "status": contract.get_status_display(),
                    "date_issued": contract.date_issued.isoformat(),
                    "time_left": time_left,
                    "info": contract.title,
                    "actions": actions_html,
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_contract_details(
    request, character_pk: int, character: Character, contract_pk: int
) -> HttpResponse:
    error_msg = None
    try:
        contract = (
            character.contracts.select_related(
                "issuer", "start_location", "end_location", "assignee"
            )
            .prefetch_related("bids")
            .get(pk=contract_pk)
        )
    except CharacterContract.DoesNotExist:
        error_msg = (
            f"Contract with pk {contract_pk} not found for character {character}"
        )
        logger.warning(error_msg)
        context = {
            "error": error_msg,
            "character": character,
        }
    else:
        try:
            has_items_included = contract.items.filter(is_included=True).exists()
            has_items_requested = contract.items.filter(is_included=False).exists()
        except ObjectDoesNotExist:
            has_items_included = False
            has_items_requested = False

        try:
            current_bid = (
                contract.bids.all().aggregate(Max("amount")).get("amount__max")
            )
            bids_count = contract.bids.count()
        except ObjectDoesNotExist:
            current_bid = None
            bids_count = None

        context = {
            "character": character,
            "contract": contract,
            "contract_summary": contract.summary(),
            "MY_DATETIME_FORMAT": MY_DATETIME_FORMAT,
            "has_items_included": has_items_included,
            "has_items_requested": has_items_requested,
            "current_bid": current_bid,
            "bids_count": bids_count,
        }
    return render(
        request,
        "memberaudit/modals/character_viewer/contract_content.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_contract_items_included_data(
    request, character_pk: int, character: Character, contract_pk: int
) -> JsonResponse:
    return _character_contract_items_data(
        request=request,
        character_pk=character_pk,
        character=character,
        contract_pk=contract_pk,
        is_included=True,
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_contract_items_requested_data(
    request, character_pk: int, character: Character, contract_pk: int
) -> JsonResponse:
    return _character_contract_items_data(
        request=request,
        character_pk=character_pk,
        character=character,
        contract_pk=contract_pk,
        is_included=False,
    )


def _character_contract_items_data(
    request,
    character_pk: int,
    character: Character,
    contract_pk: int,
    is_included: bool,
) -> JsonResponse:
    data = list()
    try:
        contract = character.contracts.prefetch_related("items").get(pk=contract_pk)
    except CharacterAsset.DoesNotExist:
        error_msg = (
            f"Contract with pk {contract_pk} not found for character {character}"
        )
        logger.warning(error_msg)
        return HttpResponseNotFound(error_msg)

    try:
        items_qs = (
            contract.items.annotate_pricing()
            .filter(is_included=is_included)
            .select_related(
                "eve_type",
                "eve_type__eve_group",
                "eve_type__eve_group__eve_category",
            )
        )
    except ObjectDoesNotExist:
        items_qs = CharacterContractItem.objects.none()

    for item in items_qs:
        name_html, name = item_icon_plus_name_html(item)
        data.append(
            {
                "id": item.record_id,
                "name": {
                    "display": name_html,
                    "sort": name,
                },
                "quantity": item.quantity if not item.is_singleton else "",
                "group": item.eve_type.eve_group.name,
                "category": item.eve_type.eve_group.eve_category.name,
                "price": item.price,
                "total": item.total,
                "is_blueprint_copy": item.is_blueprint_copy,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_corporation_history(
    request, character_pk: int, character: Character
) -> HttpResponse:
    corporation_history = list()
    try:
        corporation_history_qs = character.corporation_history.select_related(
            "corporation"
        ).order_by("start_date")
    except ObjectDoesNotExist:
        pass

    else:
        for entry in corporation_history_qs:
            if len(corporation_history) > 0:
                corporation_history[-1]["end_date"] = entry.start_date
                corporation_history[-1]["is_last"] = False

            corporation_history.append(
                {
                    "id": entry.pk,
                    "corporation_name": entry.corporation.name,
                    "start_date": entry.start_date,
                    "end_date": now(),
                    "is_last": True,
                    "is_deleted": entry.is_deleted,
                }
            )

    context = {
        "corporation_history": reversed(corporation_history),
        "has_corporation_history": len(corporation_history) > 0,
    }
    return render(
        request,
        "memberaudit/partials/character_viewer/tabs/corporation_history_2.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_implants_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        for implant in character.implants.select_related("eve_type").prefetch_related(
            "eve_type__dogma_attributes"
        ):
            implant_html = bootstrap_icon_plus_name_html(
                implant.eve_type.icon_url(
                    DEFAULT_ICON_SIZE, variant=EveType.IconVariant.REGULAR
                ),
                implant.eve_type.name,
            )
            try:
                slot_num = int(
                    implant.eve_type.dogma_attributes.get(
                        eve_dogma_attribute_id=331
                    ).value
                )
            except (ObjectDoesNotExist, AttributeError):
                slot_num = 0

            data.append(
                {
                    "id": implant.pk,
                    "implant": {"display": implant_html, "sort": slot_num},
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_loyalty_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        for entry in character.loyalty_entries.select_related("corporation"):
            corporation_html = bootstrap_icon_plus_name_html(
                entry.corporation.icon_url(DEFAULT_ICON_SIZE), entry.corporation.name
            )
            data.append(
                {
                    "id": entry.pk,
                    "corporation": {
                        "display": corporation_html,
                        "sort": entry.corporation.name,
                    },
                    "loyalty_points": entry.loyalty_points,
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_jump_clones_data(
    request, character_pk: int, character: Character
) -> HttpResponse:
    data = list()
    try:
        for jump_clone in (
            character.jump_clones.select_related(
                "location",
                "location__eve_solar_system",
                "location__eve_solar_system__eve_constellation__eve_region",
            )
            .prefetch_related("implants", "implants__eve_type__dogma_attributes")
            .all()
        ):
            if not jump_clone.location.is_empty:
                eve_solar_system = jump_clone.location.eve_solar_system
                solar_system = eve_solar_system_to_html(
                    eve_solar_system, show_region=False
                )
                region = eve_solar_system.eve_constellation.eve_region.name
            else:
                solar_system = "-"
                region = "-"

            implants_data = list()
            for obj in jump_clone.implants.all():
                dogma_attributes = {
                    attribute.eve_dogma_attribute_id: attribute.value
                    for attribute in obj.eve_type.dogma_attributes.all()
                }
                try:
                    slot_num = int(dogma_attributes[331])
                except (KeyError, TypeError):
                    slot_num = 0

                implants_data.append(
                    {
                        "name": obj.eve_type.name,
                        "icon_url": obj.eve_type.icon_url(
                            DEFAULT_ICON_SIZE, variant=EveType.IconVariant.REGULAR
                        ),
                        "slot_num": slot_num,
                    }
                )
            if implants_data:
                implants = "<br>".join(
                    bootstrap_icon_plus_name_html(
                        x["icon_url"], no_wrap_html(x["name"]), size=24
                    )
                    for x in sorted(implants_data, key=lambda k: k["slot_num"])
                )
            else:
                implants = "(none)"

            data.append(
                {
                    "id": jump_clone.pk,
                    "region": region,
                    "solar_system": solar_system,
                    "location": jump_clone.location.name_plus,
                    "implants": implants,
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


def _character_mail_headers_data(request, character, mail_headers_qs) -> JsonResponse:
    mails_data = list()
    try:
        for mail in mail_headers_qs.select_related("sender").prefetch_related(
            "recipients"
        ):
            mail_ajax_url = reverse(
                "memberaudit:character_mail_data", args=[character.pk, mail.pk]
            )
            if mail.body:
                actions_html = (
                    '<button type="button" class="btn btn-primary" '
                    'data-toggle="modal" data-target="#modalCharacterMail" '
                    f"data-ajax_mail_body={mail_ajax_url}>"
                    '<i class="fas fa-search"></i></button>'
                )
            else:
                actions_html = ""

            mails_data.append(
                {
                    "mail_id": mail.mail_id,
                    "from": mail.sender.name_plus,
                    "to": ", ".join(
                        sorted([obj.name_plus for obj in mail.recipients.all()])
                    ),
                    "subject": mail.subject,
                    "sent": mail.timestamp.isoformat(),
                    "action": actions_html,
                    "is_read": mail.is_read,
                    "is_unread_str": yesno_str(mail.is_read is False),
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(mails_data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_mail_headers_by_label_data(
    request, character_pk: int, character: Character, label_id: int
) -> JsonResponse:
    if label_id == MAIL_LABEL_ID_ALL_MAILS:
        mail_headers_qs = character.mails.all()
    else:
        mail_headers_qs = character.mails.filter(labels__label_id=label_id)

    return _character_mail_headers_data(request, character, mail_headers_qs)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_mail_headers_by_list_data(
    request, character_pk: int, character: Character, list_id: int
) -> JsonResponse:
    mail_headers_qs = character.mails.filter(recipients__id=list_id)
    return _character_mail_headers_data(request, character, mail_headers_qs)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_mail_data(
    request, character_pk: int, character: Character, mail_pk: int
) -> JsonResponse:
    try:
        mail = (
            character.mails.select_related("sender")
            .prefetch_related("recipients")
            .get(pk=mail_pk)
        )
    except CharacterMail.DoesNotExist:
        error_msg = f"Mail with pk {mail_pk} not found for character {character}"
        logger.warning(error_msg)
        return HttpResponseNotFound(error_msg)

    recipients = sorted(
        [
            {
                "name": obj.name_plus,
                "link": link_html(obj.external_url(), obj.name_plus),
            }
            for obj in mail.recipients.all()
        ],
        key=lambda k: k["name"],
    )

    data = {
        "mail_id": mail.mail_id,
        "labels": list(mail.labels.values_list("label_id", flat=True)),
        "from": link_html(mail.sender.external_url(), mail.sender.name_plus),
        "to": ", ".join([obj["link"] for obj in recipients]),
        "subject": mail.subject,
        "sent": mail.timestamp.isoformat(),
        "body": mail.body_html if mail.body != "" else "(no data yet)",
    }
    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_skillqueue_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    data = list()
    try:
        for row in character.skillqueue.select_related("eve_type").filter(
            character_id=character_pk
        ):
            level_roman = MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[row.finished_level]
            skill_str = f"{row.eve_type.name}&nbsp;{level_roman}"
            if row.is_active:
                skill_str += " [ACTIVE]"

            if row.finish_date:
                finish_date_humanized = humanize.naturaltime(
                    dt.datetime.now()
                    + dt.timedelta(
                        seconds=(
                            row.finish_date.timestamp() - dt.datetime.now().timestamp()
                        )
                    )
                )
                finish_date_str = (
                    f"{row.finish_date.strftime(DATETIME_FORMAT)} "
                    f"({finish_date_humanized})"
                )
                finish_date_sort = row.finish_date.isoformat()
            else:
                finish_date_str = gettext("(training not active)")
                finish_date_sort = None

            data.append(
                {
                    "position": row.queue_position + 1,
                    "skill": skill_str,
                    "finished": {
                        "display": finish_date_str,
                        "sort": finish_date_sort,
                    },
                    "is_active": row.is_active,
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_skill_sets_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    def create_data_row(check, group) -> dict:
        if group:
            group_name = (
                group.name_plus if group.is_active else group.name + " [Not active]"
            )
        else:
            group_name = UNGROUPED_SKILL_SET

        url = (
            check.skill_set.ship_type.icon_url(
                DEFAULT_ICON_SIZE, variant=EveType.IconVariant.REGULAR
            )
            if check.skill_set.ship_type
            else eveimageserver.type_icon_url(
                SKILL_SET_DEFAULT_ICON_TYPE_ID, size=DEFAULT_ICON_SIZE
            )
        )
        ship_icon = f'<img width="24" heigh="24" src="{url}"/>'
        failed_required_skills = compile_failed_skills(
            check.failed_required_skills, "required_level"
        )
        has_required = (
            not bool(failed_required_skills)
            if failed_required_skills is not None
            else None
        )
        failed_recommended_skills = compile_failed_skills(
            check.failed_recommended_skills, "recommended_level"
        )
        has_recommended = (
            not bool(failed_recommended_skills)
            if failed_recommended_skills is not None
            else None
        )
        ajax_children_url = reverse(
            "memberaudit:character_skill_set_details",
            args=[character.pk, check.skill_set_id],
        )

        actions_html = (
            '<button type="button" class="btn btn-primary" '
            'data-toggle="modal" data-target="#modalCharacterSkillSetDetails" '
            f"data-ajax_skill_set_detail={ ajax_children_url }>"
            '<i class="fas fa-search"></i></button>'
        )

        return {
            "id": check.id,
            "group": group_name,
            "skill_set": ship_icon + "&nbsp;&nbsp;" + check.skill_set.name,
            "skill_set_name": check.skill_set.name,
            "is_doctrine_str": yesnonone_str(group.is_doctrine if group else False),
            "failed_required_skills": format_failed_skills(failed_required_skills),
            "has_required": has_required,
            "has_required_str": yesnonone_str(has_required),
            "failed_recommended_skills": format_failed_skills(
                failed_recommended_skills
            ),
            "has_recommended": has_recommended,
            "has_recommended_str": yesnonone_str(has_recommended),
            "action": actions_html,
        }

    def compile_failed_skills(failed_skills, level_name) -> Optional[list]:
        failed_skills = sorted(
            failed_skills.values("eve_type__name", level_name),
            key=lambda k: k["eve_type__name"].lower(),
        )
        return [
            bootstrap_label_html(
                format_html(
                    "{}&nbsp;{}",
                    obj["eve_type__name"],
                    MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[obj[level_name]],
                ),
                "default",
            )
            for obj in failed_skills
        ]

    def format_failed_skills(skills) -> str:
        return " ".join(skills) if skills else "-"

    data = list()
    try:
        for check in character.skill_set_checks.filter(
            skill_set__is_visible=True
        ).select_related(
            "skill_set", "skill_set__ship_type", "skill_set__ship_type__eve_group"
        ):
            if not check.skill_set.groups.exists():
                data.append(create_data_row(check, None))
            else:
                for group in check.skill_set.groups.all():
                    data.append(create_data_row(check, group))

    except ObjectDoesNotExist:
        pass

    data = sorted(data, key=lambda k: (k["group"].lower(), k["skill_set_name"].lower()))
    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_skill_set_details(
    request, character_pk: int, character: Character, skill_set_pk: int
) -> HttpResponse:

    skill_set = SkillSet.objects.get(id=skill_set_pk)
    skill_set_skills = SkillSetSkill.objects.filter(skill_set_id=skill_set_pk)

    out_data = list()

    url = (
        skill_set.ship_type.icon_url(ICON_SIZE_64, variant=EveType.IconVariant.REGULAR)
        if skill_set.ship_type
        else eveimageserver.type_icon_url(
            SKILL_SET_DEFAULT_ICON_TYPE_ID, size=ICON_SIZE_64
        )
    )

    for skill in skill_set_skills:
        cs = (
            character.skills.select_related("eve_type")
            .filter(eve_type_id=skill.eve_type_id)
            .first()
        )

        recommended_level_str = "-"
        required_level_str = "-"
        current_str = "-"
        result_icon = ICON_FAILED
        met_required = True

        if cs:
            current_str = MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[cs.active_skill_level]

        if skill.recommended_level:
            recommended_level_str = MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[
                skill.recommended_level
            ]

        if skill.required_level:
            required_level_str = MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[skill.required_level]

        if not cs:
            result_icon = ICON_FAILED
            met_required = False
        else:
            if (
                skill.required_level
                and not skill.recommended_level
                and cs.active_skill_level >= skill.required_level
            ):
                result_icon = ICON_FULL
            elif (
                skill.recommended_level
                and cs.active_skill_level >= skill.recommended_level
            ):
                result_icon = ICON_FULL
            elif skill.required_level and cs.active_skill_level >= skill.required_level:
                result_icon = ICON_PARTIAL
            else:
                met_required = False

        out_data.append(
            {
                "name": skill.eve_type.name,
                "required": required_level_str,
                "recommended": recommended_level_str,
                "current": current_str,
                "result_icon": result_icon,
                "met_required": met_required,
            }
        )

    met_all_required = True
    for data in out_data:
        if not data["met_required"]:
            met_all_required = False
            break

    out_data = sorted(out_data, key=lambda k: (k["name"].lower()))
    context = {
        "name": skill_set.name,
        "description": skill_set.description,
        "ship_url": url,
        "skills": out_data,
        "met_all_required": met_all_required,
        "icon_failed": ICON_FAILED,
        "icon_partial": ICON_PARTIAL,
        "icon_full": ICON_FULL,
        "icon_met_all_required": ICON_MET_ALL_REQUIRED,
    }

    return render(
        request,
        "memberaudit/modals/character_viewer/skill_set_content.html",
        context,
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_attribute_data(
    request, character_pk: int, character: Character
) -> HttpResponse:

    try:
        character_attributes = character.attributes
    except ObjectDoesNotExist:
        character_attributes = None

    context = {"character_attributes": character_attributes}

    return render(
        request,
        "memberaudit/partials/character_viewer/tabs/character_attributes_content.html",
        context,
    )


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_skills_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    skills_data = list()
    try:
        for skill in character.skills.select_related(
            "eve_type", "eve_type__eve_group"
        ).filter(active_skill_level__gte=1):
            level_str = MAP_SKILL_LEVEL_ARABIC_TO_ROMAN[skill.active_skill_level]
            skill_name = f"{skill.eve_type.name} {level_str}"
            skills_data.append(
                {
                    "group": skill.eve_type.eve_group.name,
                    "skill": skill.eve_type.name,
                    "skill_name": f"{skill_name} - {skill.eve_type_id}",
                    "level": skill.active_skill_level,
                    "level_str": level_str,
                }
            )
    except ObjectDoesNotExist:
        pass

    return JsonResponse(skills_data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_wallet_journal_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    wallet_data = list()
    try:
        for row in character.wallet_journal.select_related(
            "first_party", "second_party"
        ).all():
            first_party = row.first_party.name if row.first_party else "-"
            second_party = row.second_party.name if row.second_party else "-"
            wallet_data.append(
                {
                    "date": row.date.isoformat(),
                    "ref_type": row.ref_type.replace("_", " ").title(),
                    "first_party": first_party,
                    "second_party": second_party,
                    "amount": float(row.amount),
                    "balance": float(row.balance),
                    "description": row.description,
                    "reason": row.reason,
                }
            )
    except ObjectDoesNotExist:
        pass
    return JsonResponse(wallet_data, safe=False)


@login_required
@permission_required("memberaudit.basic_access")
@fetch_character_if_allowed()
def character_wallet_transactions_data(
    request, character_pk: int, character: Character
) -> JsonResponse:
    wallet_data = list()
    try:
        for row in character.wallet_transactions.select_related(
            "client", "eve_type", "location"
        ).all():
            buy_or_sell = gettext_lazy("Buy") if row.is_buy else gettext_lazy("Sell")
            wallet_data.append(
                {
                    "date": row.date.isoformat(),
                    "quantity": row.quantity,
                    "type": row.eve_type.name,
                    "unit_price": float(row.unit_price),
                    "total": float(
                        row.unit_price * row.quantity * (-1 if row.is_buy else 1)
                    ),
                    "client": row.client.name,
                    "location": row.location.name,
                    "is_buy": row.is_buy,
                    "buy_or_sell": buy_or_sell,
                }
            )
    except ObjectDoesNotExist:
        pass
    return JsonResponse(wallet_data, safe=False)


#############################
# Section: Character Finder


@login_required
@permission_required("memberaudit.finder_access")
def character_finder(request) -> HttpResponse:
    context = {
        "page_title": "Character Finder",
    }
    return render(
        request,
        "memberaudit/character_finder.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.finder_access")
def character_finder_data(request) -> JsonResponse:
    character_list = list()
    for character in Character.objects.user_has_access(
        user=request.user
    ).select_related(
        "character_ownership__character",
        "character_ownership__user",
        "character_ownership__user__profile__main_character",
        "character_ownership__user__profile__state",
        "location__location",
        "location__eve_solar_system",
        "location__eve_solar_system__eve_constellation__eve_region",
    ):
        auth_character = character.character_ownership.character
        character_viewer_url = reverse(
            "memberaudit:character_viewer", args=[character.pk]
        )
        actions_html = fontawesome_link_button_html(
            url=character_viewer_url,
            fa_code="fas fa-search",
            button_type="primary",
        )
        alliance_name = (
            auth_character.alliance_name if auth_character.alliance_name else ""
        )
        character_organization = format_html(
            "{}<br><em>{}</em>", auth_character.corporation_name, alliance_name
        )
        user_profile = character.character_ownership.user.profile
        try:
            main_html = bootstrap_icon_plus_name_html(
                user_profile.main_character.portrait_url(),
                user_profile.main_character.character_name,
                avatar=True,
            )
            main_corporation = user_profile.main_character.corporation_name
            main_alliance = (
                user_profile.main_character.alliance_name
                if user_profile.main_character.alliance_name
                else ""
            )
            main_organization = format_html(
                "{}<br><em>{}</em>", auth_character.corporation_name, alliance_name
            )

        except AttributeError:
            main_alliance = main_organization = main_corporation = main_html = ""

        text = format_html(
            "{}&nbsp;{}",
            mark_safe('&nbsp;<i class="fas fa-crown" title="Main character">')
            if character.is_main
            else "",
            mark_safe('&nbsp;<i class="far fa-eye" title="Shared character">')
            if character.is_shared
            else "",
        )
        character_html = bootstrap_icon_plus_name_html(
            auth_character.portrait_url(),
            auth_character.character_name,
            avatar=True,
            url=character_viewer_url,
            text=text,
        )

        try:
            location_name = (
                character.location.location.name if character.location.location else ""
            )
            solar_system_html = eve_solar_system_to_html(
                character.location.eve_solar_system
            )
            location_html = format_html("{}<br>{}", location_name, solar_system_html)
            solar_system_name = character.location.eve_solar_system.name
            region_name = (
                character.location.eve_solar_system.eve_constellation.eve_region.name
            )
        except ObjectDoesNotExist:
            location_html = ""
            solar_system_name = ""
            region_name = ""

        alliance_name = (
            auth_character.alliance_name if auth_character.alliance_name else ""
        )
        character_list.append(
            {
                "character_pk": character.pk,
                "character": {
                    "display": character_html,
                    "sort": auth_character.character_name,
                },
                "character_organization": character_organization,
                "main_character": main_html,
                "main_organization": main_organization,
                "state_name": user_profile.state.name,
                "location": location_html,
                "actions": actions_html,
                "alliance_name": alliance_name,
                "corporation_name": auth_character.corporation_name,
                "solar_system_name": solar_system_name,
                "region_name": region_name,
                "main_alliance_name": main_alliance,
                "main_corporation_name": main_corporation,
                "main_str": yesno_str(character.is_main),
            }
        )
    return JsonResponse(character_list, safe=False)


#############################
# Section: Reports


@login_required
@permission_required("memberaudit.reports_access")
def reports(request) -> HttpResponse:
    context = {
        "page_title": "Reports",
    }
    return render(
        request,
        "memberaudit/reports.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("memberaudit.reports_access")
def user_compliance_report_data(request) -> JsonResponse:
    users_and_character_counts = (
        General.accessible_users(request.user)
        .exclude(profile__state__pk=get_guest_state_pk())
        .annotate(total_chars=Count("character_ownerships__character", distinct=True))
        .annotate(
            unregistered_chars=Count(
                "character_ownerships",
                filter=Q(character_ownerships__memberaudit_character=None),
                distinct=True,
            )
        )
        .select_related("profile__main_character", "profile__state")
    )
    user_data = list()
    for user in users_and_character_counts:
        if user.profile.main_character:
            main_character = user.profile.main_character
            if user == request.user or request.user.has_perm(
                "memberaudit.characters_access"
            ):
                try:
                    character = main_character.character_ownership.memberaudit_character
                except ObjectDoesNotExist:
                    url = None
                else:
                    url = reverse("memberaudit:character_viewer", args=[character.pk])
            else:
                url = None
            main_name = main_character.character_name
            main_html = bootstrap_icon_plus_name_html(
                main_character.portrait_url(),
                main_character.character_name,
                avatar=True,
                url=url,
            )
            corporation_name = main_character.corporation_name
            organization_html = create_main_organization_html(main_character)
            alliance_name = (
                main_character.alliance_name if main_character.alliance_name else ""
            )
            is_compliant = user.unregistered_chars == 0
        else:
            main_name = user.username
            main_html = bootstrap_icon_plus_name_html(
                eveimageserver.character_portrait_url(1, size=DEFAULT_ICON_SIZE),
                main_name,
                avatar=True,
                url=url,
            )
            alliance_name = organization_html = corporation_name = ""
            is_compliant = False

        is_registered = user.unregistered_chars < user.total_chars
        user_data.append(
            {
                "id": user.pk,
                "main": {
                    "display": main_html,
                    "sort": main_name,
                },
                "organization": {
                    "display": organization_html,
                    "sort": corporation_name,
                },
                "state": user.profile.state.name,
                "corporation_name": corporation_name,
                "alliance_name": alliance_name,
                "total_chars": user.total_chars,
                "unregistered_chars": user.unregistered_chars,
                "is_registered": is_registered,
                "registered_str": yesno_str(is_registered),
                "is_compliant": is_compliant,
                "compliance_str": yesno_str(is_compliant),
            }
        )
    return JsonResponse(user_data, safe=False)


@login_required
@permission_required("memberaudit.reports_access")
def corporation_compliance_report_data(request) -> JsonResponse:
    relevant_user_ids = list(
        General.accessible_users(request.user)
        .exclude(profile__state__pk=get_guest_state_pk())
        .values_list("id", flat=True)
    )
    corporations = (
        EveCharacter.objects.select_related(
            "userprofile",
            "userprofile__user__character_ownerships__character",
            "userprofile__user__character_ownerships",
        )
        .filter(userprofile__in=relevant_user_ids)
        .values(
            "corporation_id",
            "corporation_name",
            "alliance_id",
            "alliance_name",
            "alliance_ticker",
        )
        .distinct()
        .annotate(mains_count=Count("userprofile", distinct=True))
        .annotate(
            characters_count=Count(
                "userprofile__user__character_ownerships__character", distinct=True
            )
        )
        .annotate(
            unregistered_count=Count(
                "userprofile__user__character_ownerships",
                filter=Q(
                    userprofile__user__character_ownerships__memberaudit_character=None
                ),
                distinct=True,
            )
        )
    )
    data = list()
    for corporation in corporations:
        organization_name = "{}{}".format(
            corporation["corporation_name"],
            f" [{corporation['alliance_ticker']}]"
            if corporation["alliance_ticker"]
            else "",
        )
        alliance_name = (
            corporation["alliance_name"] if corporation["alliance_name"] else ""
        )
        compliance_p = (
            round(
                (corporation["characters_count"] - corporation["unregistered_count"])
                / corporation["characters_count"]
                * 100
            )
            if corporation["characters_count"] > 0
            else 0
        )
        is_compliant = compliance_p == 100
        data.append(
            {
                "id": corporation["corporation_id"],
                "organization_html": {
                    "display": bootstrap_icon_plus_name_html(
                        icon_url=eveimageserver.corporation_logo_url(
                            corporation_id=corporation["corporation_id"],
                            size=DEFAULT_ICON_SIZE,
                        ),
                        name=organization_name,
                    ),
                    "sort": corporation["corporation_name"],
                },
                "corporation_name": corporation["corporation_name"],
                "alliance_name": alliance_name,
                "mains_count": corporation["mains_count"],
                "characters_count": corporation["characters_count"],
                "unregistered_count": corporation["unregistered_count"],
                "compliance_percent": compliance_p,
                "is_compliant": is_compliant,
                "is_partly_compliant": compliance_p >= 85,
                "is_compliant_str": yesno_str(is_compliant),
            }
        )
    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.reports_access")
def skill_sets_report_data(request) -> JsonResponse:
    def create_data_row(group, character) -> dict:
        user = character.character_ownership.user
        auth_character = character.character_ownership.character
        main_character = user.profile.main_character
        if main_character:
            main_name = main_character.character_name
            main_html = bootstrap_icon_plus_name_html(
                user.profile.main_character.portrait_url(), main_name, avatar=True
            )
            main_corporation = main_character.corporation_name
            main_alliance = (
                main_character.alliance_name if main_character.alliance_name else ""
            )
            organization_html = format_html(
                "{}{}",
                main_corporation,
                f" [{main_character.alliance_ticker}]"
                if main_character.alliance_name
                else "",
            )
        else:
            main_html = main_name = ""
            main_corporation = main_alliance = organization_html = ""
        character_viewer_url = "{}?tab=skill_sets".format(
            reverse("memberaudit:character_viewer", args=[character.pk])
        )
        character_html = bootstrap_icon_plus_name_html(
            auth_character.portrait_url(),
            auth_character.character_name,
            avatar=True,
            url=character_viewer_url,
        )
        group_pk = group.pk if group else 0
        has_required = [
            bootstrap_icon_plus_name_html(
                obj.skill_set.ship_type.icon_url(
                    DEFAULT_ICON_SIZE, variant=EveType.IconVariant.REGULAR
                )
                if obj.skill_set.ship_type
                else eveimageserver.type_icon_url(
                    SKILL_SET_DEFAULT_ICON_TYPE_ID, size=DEFAULT_ICON_SIZE
                ),
                obj.skill_set.name,
            )
            for obj in skill_set_qs
        ]
        has_required_html = (
            "<br>".join(has_required)
            if has_required
            else '<i class="fas fa-times boolean-icon-false"></i>'
        )
        return {
            "id": f"{group_pk}_{character.pk}",
            "group": group.name_plus if group else UNGROUPED_SKILL_SET,
            "main": main_name,
            "main_html": main_html,
            "state": user.profile.state.name,
            "organization_html": organization_html,
            "corporation": main_corporation,
            "alliance": main_alliance,
            "character": character.character_ownership.character.character_name,
            "character_html": character_html,
            "has_required": has_required_html,
            "has_required_str": yesno_str(bool(has_required)),
            "is_doctrine_str": yesno_str(group.is_doctrine if group else False),
        }

    data = list()
    relevant_user_ids = list(
        General.accessible_users(request.user).exclude(
            profile__state__pk=get_guest_state_pk()
        )
    )
    character_qs = (
        Character.objects.select_related(
            "character_ownership__user",
            "character_ownership__user__profile__main_character",
            "character_ownership__character",
        )
        .prefetch_related("skill_set_checks")
        .filter(character_ownership__user__in=relevant_user_ids)
    )
    my_select_related = (
        "skill_set",
        "skill_set__ship_type",
        # "skill_set__ship_type__eve_group",
    )
    for group in SkillSetGroup.objects.all():
        for character in character_qs:
            skill_set_qs = (
                character.skill_set_checks.select_related(*my_select_related)
                .filter(skill_set__groups=group, failed_required_skills__isnull=True)
                .order_by("skill_set__name")
            )
            data.append(create_data_row(group, character))

    for character in character_qs:
        if (
            character.skill_set_checks.select_related("skill_set")
            .filter(skill_set__groups__isnull=True)
            .exists()
        ):
            skill_set_qs = (
                character.skill_set_checks.select_related(*my_select_related)
                .filter(
                    skill_set__groups__isnull=True, failed_required_skills__isnull=True
                )
                .order_by("skill_set__name")
            )
            data.append(create_data_row(None, character))

    return JsonResponse(data, safe=False)


@login_required
@permission_required("memberaudit.exports_access")
def data_export(request):
    topics = data_exporters.topics_and_export_files()
    context = {
        "page_title": "Data Export",
        "topics": topics,
        "character_count": Character.objects.count(),
        "minutes_until_next_update": MEMBERAUDIT_DATA_EXPORT_MIN_UPDATE_AGE,
    }
    return render(
        request, "memberaudit/data_export.html", add_common_context(request, context)
    )


@login_required
@permission_required("memberaudit.exports_access")
def download_export_file(request, topic: str) -> FileResponse:
    exporter = data_exporters.DataExporter.create_exporter(topic)
    destination = data_exporters.default_destination()
    zip_file = destination / exporter.output_basename.with_suffix(".zip")
    if not zip_file.exists():
        raise Http404(f"Could not find export file for {topic}")
    logger.info("Returning file %s for download of topic %s", zip_file, topic)
    return FileResponse(zip_file.open("rb"))


@login_required
@permission_required("memberaudit.exports_access")
def data_export_run_update(request, topic: str):
    tasks.export_data_for_topic.delay(topic=topic, user_pk=request.user.pk)
    format_html
    messages_plus.info(
        request,
        format_html(
            "Data export for topic <strong>{}</strong> has been started. "
            "This can take a couple of minutes. "
            "You will get a notification once it is completed.",
            topic,
        ),
    )
    return redirect("memberaudit:data_export")
