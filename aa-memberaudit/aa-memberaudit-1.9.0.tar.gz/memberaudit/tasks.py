import inspect
import random
from typing import Optional

from bravado.exception import HTTPBadGateway, HTTPGatewayTimeout, HTTPServiceUnavailable
from celery import chain, shared_task

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now
from esi.models import Token
from eveuniverse.models import EveEntity, EveMarketPrice

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce
from app_utils.esi import EsiErrorLimitExceeded, EsiOffline, fetch_esi_status
from app_utils.logging import LoggerAddTag

from . import __title__
from .app_settings import (
    MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
    MEMBERAUDIT_LOG_UPDATE_STATS,
    MEMBERAUDIT_TASKS_MAX_ASSETS_PER_PASS,
    MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT,
    MEMBERAUDIT_TASKS_TIME_LIMIT,
    MEMBERAUDIT_UPDATE_STALE_RING_2,
)
from .core import data_exporters
from .models import (
    Character,
    CharacterAsset,
    CharacterContract,
    CharacterMail,
    CharacterUpdateStatus,
    Location,
    MailEntity,
)

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

DEFAULT_TASK_PRIORITY = 6

# params for all tasks
TASK_DEFAULT_KWARGS = {
    "time_limit": MEMBERAUDIT_TASKS_TIME_LIMIT,
    "max_retries": 3,
}

# params for tasks that make ESI calls
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


def _retry_if_esi_is_down(self):
    """Retries the task if ESI is not online or not within the error threshold"""
    try:
        fetch_esi_status().raise_for_status()
    except EsiOffline as ex:
        countdown = (10 + int(random.uniform(1, 10))) * 60
        logger.warning(
            "ESI appears to be offline. Trying again in %d minutes.", countdown
        )
        raise self.retry(countdown=countdown) from ex
    except EsiErrorLimitExceeded as ex:
        logger.warning(
            "ESI error limit threshold reached. Trying again in %s seconds", ex.retry_in
        )
        raise self.retry(countdown=ex.retry_in) from ex


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def run_regular_updates(self) -> None:
    """Main task to be run on a regular basis to keep everyting updated and running"""
    _retry_if_esi_is_down(self)
    update_market_prices.apply_async(priority=DEFAULT_TASK_PRIORITY)
    update_all_characters.apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_DEFAULT_KWARGS)
def update_all_characters(force_update: bool = False) -> None:
    """Start the update of all registered characters

    Args:
    - force_update: When set to True will always update regardless of stale status
    """
    if MEMBERAUDIT_LOG_UPDATE_STATS:
        stats = CharacterUpdateStatus.objects.statistics()
        logger.info(f"Update statistics: {stats}")

    for character_pk in Character.objects.values_list("pk", flat=True):
        update_character.apply_async(
            kwargs={"character_pk": character_pk, "force_update": force_update},
            priority=DEFAULT_TASK_PRIORITY,
        )


# Main character update tasks


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_character(self, character_pk: int, force_update: bool = False) -> bool:
    """Start respective update tasks for all stale sections of a character

    Args:
    - character_pk: PL of character to update
    - force_update: When set to True will always update regardless of stale status

    Returns:
    - True when update was conducted
    - False when no updated was needed
    """
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    all_sections = set(Character.UpdateSection.values)
    needs_update = force_update
    for section in all_sections:
        needs_update |= character.is_update_section_stale(section)

    if not needs_update:
        logger.info("%s: No update required", character)
        return False

    logger.info(
        "%s: Starting %s character update", character, "forced" if force_update else ""
    )
    sections = all_sections.difference(
        {
            Character.UpdateSection.ASSETS,
            Character.UpdateSection.MAILS,
            Character.UpdateSection.CONTACTS,
            Character.UpdateSection.CONTRACTS,
            Character.UpdateSection.SKILL_SETS,
            Character.UpdateSection.SKILLS,
            Character.UpdateSection.WALLET_JOURNAL,
        }
    )
    for section in sorted(sections):
        if force_update or character.is_update_section_stale(section):
            update_character_section.apply_async(
                kwargs={
                    "character_pk": character.pk,
                    "section": section,
                    "force_update": force_update,
                    "root_task_id": self.request.parent_id,
                    "parent_task_id": self.request.id,
                },
                priority=DEFAULT_TASK_PRIORITY,
            )

    if force_update or character.is_update_section_stale(Character.UpdateSection.MAILS):
        update_character_mails.apply_async(
            kwargs={
                "character_pk": character.pk,
                "force_update": force_update,
                "root_task_id": self.request.parent_id,
                "parent_task_id": self.request.id,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )
    if force_update or character.is_update_section_stale(
        Character.UpdateSection.CONTACTS
    ):
        update_character_contacts.apply_async(
            kwargs={
                "character_pk": character.pk,
                "force_update": force_update,
                "root_task_id": self.request.parent_id,
                "parent_task_id": self.request.id,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )
    if force_update or character.is_update_section_stale(
        Character.UpdateSection.CONTRACTS
    ):
        update_character_contracts.apply_async(
            kwargs={
                "character_pk": character.pk,
                "force_update": force_update,
                "root_task_id": self.request.parent_id,
                "parent_task_id": self.request.id,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )

    if force_update or character.is_update_section_stale(
        Character.UpdateSection.WALLET_JOURNAL
    ):
        update_character_wallet_journal.apply_async(
            kwargs={
                "character_pk": character.pk,
                "root_task_id": self.request.parent_id,
                "parent_task_id": self.request.id,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )

    if force_update or character.is_update_section_stale(
        Character.UpdateSection.ASSETS
    ):
        update_character_assets.apply_async(
            kwargs={
                "character_pk": character.pk,
                "force_update": force_update,
                "root_task_id": self.request.parent_id,
                "parent_task_id": self.request.id,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )

    if (
        force_update
        or character.is_update_section_stale(Character.UpdateSection.SKILLS)
        or character.is_update_section_stale(Character.UpdateSection.SKILL_SETS)
    ):
        chain(
            update_character_section.si(
                character.pk,
                Character.UpdateSection.SKILLS,
                force_update,
                self.request.parent_id,
                self.request.id,
            ),
            update_character_section.si(
                character.pk,
                Character.UpdateSection.SKILL_SETS,
                force_update,
                self.request.parent_id,
                self.request.id,
            ),
        ).apply_async(priority=DEFAULT_TASK_PRIORITY)

    return True


# Update sections


@shared_task(**{**TASK_ESI_KWARGS, **{"base": QueueOnce}})
def update_character_section(
    self,
    character_pk: int,
    section: str,
    force_update: bool = False,
    root_task_id: str = None,
    parent_task_id: str = None,
    **kwargs,
) -> None:
    """Task that updates the section of a character"""
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    character.reset_update_section(section, root_task_id, parent_task_id)
    logger.info(
        "%s: Updating %s", character, Character.UpdateSection.display_name(section)
    )
    update_method = getattr(character, Character.UpdateSection.method_name(section))
    args = [self, character, section, update_method]
    if not kwargs:
        kwargs = {}

    method_signature = inspect.signature(update_method)
    if "force_update" in method_signature.parameters:
        kwargs["force_update"] = force_update

    _character_update_with_error_logging(*args, **kwargs)
    _log_character_update_success(character, section)


def _character_update_with_error_logging(
    self, character: Character, section: str, method: object, *args, **kwargs
):
    """Allows catching and logging of any exceptions occuring
    during an character update
    """
    try:
        return method(*args, **kwargs)
    except Exception as ex:
        error_message = f"{type(ex).__name__}: {str(ex)}"
        logger.error(
            "%s: %s: Error ocurred: %s",
            character,
            Character.UpdateSection.display_name(section),
            error_message,
            exc_info=True,
        )
        CharacterUpdateStatus.objects.update_or_create(
            character=character,
            section=section,
            defaults={
                "is_success": False,
                "last_error_message": error_message,
                "finished_at": now(),
            },
        )
        raise ex


def _log_character_update_success(character: Character, section: str):
    """Logs character update success for a section"""
    logger.info(
        "%s: %s update completed",
        character,
        Character.UpdateSection.display_name(section),
    )
    CharacterUpdateStatus.objects.update_or_create(
        character=character,
        section=section,
        defaults={"is_success": True, "last_error_message": "", "finished_at": now()},
    )


@shared_task(**TASK_ESI_KWARGS)
def update_unresolved_eve_entities(
    self, character_pk: int, section: str, last_in_chain: bool = False
) -> None:
    """Bulk resolved all unresolved EveEntity objects in database and logs errors to respective section

    Optionally logs success for given update section
    """
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self, character, section, EveEntity.objects.bulk_update_new_esi
    )
    if last_in_chain:
        _log_character_update_success(character, section)


# Special tasks for updating assets


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_assets(
    character_pk: int,
    force_update: bool = False,
    root_task_id: str = None,
    parent_task_id: str = None,
) -> None:
    """Main tasks for updating the character's assets"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    logger.info(
        "%s: Updating %s",
        character,
        Character.UpdateSection.display_name(Character.UpdateSection.ASSETS),
    )
    character.reset_update_section(
        section=Character.UpdateSection.ASSETS,
        root_task_id=root_task_id,
        parent_task_id=parent_task_id,
    )
    chain(
        assets_build_list_from_esi.s(character.pk, force_update),
        assets_preload_objects.s(character.pk),
        assets_create_parents.s(character.pk),
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_ESI_KWARGS)
def assets_build_list_from_esi(
    self, character_pk: int, force_update: bool = False
) -> dict:
    """Building asset list"""
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    asset_list = _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.ASSETS,
        character.assets_build_list_from_esi,
        force_update,
    )
    return asset_list


@shared_task(**TASK_ESI_KWARGS)
def assets_preload_objects(self, asset_list: dict, character_pk: int) -> Optional[dict]:
    """Task for preloading asset objects"""
    if asset_list is None:
        return None

    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.ASSETS,
        character.assets_preload_objects,
        asset_list,
    )
    return asset_list


@shared_task(**TASK_ESI_KWARGS)
def assets_create_parents(
    self, asset_list: list, character_pk: int, cycle: int = 1
) -> None:
    """creates the parent assets from given asset_list

    Parent assets are assets attached directly to a Location object (e.g. station)

    This task will recursively call itself until all possible parent assets
    from the asset list have been created.
    Then call another task to create child assets.
    """
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    if asset_list is None:
        _log_character_update_success(character, Character.UpdateSection.ASSETS)
        return

    logger.info("%s: Creating parent assets - pass %s", character, cycle)

    assets_flat = {int(x["item_id"]): x for x in asset_list}
    new_assets = list()
    with transaction.atomic():
        if cycle == 1:
            character.assets.all().delete()

        location_ids = set(Location.objects.values_list("id", flat=True))
        parent_asset_ids = {
            item_id
            for item_id, asset_info in assets_flat.items()
            if asset_info.get("location_id")
            and asset_info["location_id"] in location_ids
        }
        for item_id in parent_asset_ids:
            item = assets_flat[item_id]
            new_assets.append(
                CharacterAsset(
                    character=character,
                    item_id=item_id,
                    location_id=item["location_id"],
                    eve_type_id=item.get("type_id"),
                    name=item.get("name"),
                    is_blueprint_copy=item.get("is_blueprint_copy"),
                    is_singleton=item.get("is_singleton"),
                    location_flag=item.get("location_flag"),
                    quantity=item.get("quantity"),
                )
            )
            assets_flat.pop(item_id)
            if len(new_assets) >= MEMBERAUDIT_TASKS_MAX_ASSETS_PER_PASS:
                break

        logger.info("%s: Writing %s parent assets", character, len(new_assets))
        # TODO: `ignore_conflicts=True` needed as workaround to compensate for
        # occasional duplicate FK constraint errors. Needs to be investigated
        CharacterAsset.objects.bulk_create(
            new_assets,
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
            ignore_conflicts=True,
        )

    if len(parent_asset_ids) > len(new_assets):
        # there are more parent assets to create
        assets_create_parents.apply_async(
            kwargs={
                "asset_list": list(assets_flat.values()),
                "character_pk": character.pk,
                "cycle": cycle + 1,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )
    else:
        # all parent assets created
        if assets_flat:
            assets_create_children.apply_async(
                kwargs={
                    "asset_list": list(assets_flat.values()),
                    "character_pk": character.pk,
                },
                priority=DEFAULT_TASK_PRIORITY,
            )
        else:
            _log_character_update_success(character, Character.UpdateSection.ASSETS)


@shared_task(**TASK_ESI_KWARGS)
def assets_create_children(
    self, asset_list: dict, character_pk: int, cycle: int = 1
) -> None:
    """Created child assets from given asset list

    Child assets are assets located within other assets (aka containers)

    This task will recursively call itself until all possible assets from the
    asset list are included into the asset tree
    """
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    logger.info("%s: Creating child assets - pass %s", character, cycle)

    # for debug
    # character._store_list_to_disk(asset_list, f"child_asset_list_{cycle}")

    new_assets = list()
    assets_flat = {int(x["item_id"]): x for x in asset_list}
    with transaction.atomic():
        parent_asset_ids = set(character.assets.values_list("item_id", flat=True))
        child_asset_ids = {
            item_id
            for item_id, item in assets_flat.items()
            if item.get("location_id") and item["location_id"] in parent_asset_ids
        }
        for item_id in child_asset_ids:
            item = assets_flat[item_id]
            new_assets.append(
                CharacterAsset(
                    character=character,
                    item_id=item_id,
                    parent=character.assets.get(item_id=item["location_id"]),
                    eve_type_id=item.get("type_id"),
                    name=item.get("name"),
                    is_blueprint_copy=item.get("is_blueprint_copy"),
                    is_singleton=item.get("is_singleton"),
                    location_flag=item.get("location_flag"),
                    quantity=item.get("quantity"),
                )
            )
            assets_flat.pop(item_id)
            if len(new_assets) >= MEMBERAUDIT_TASKS_MAX_ASSETS_PER_PASS:
                break

        if new_assets:
            logger.info("%s: Writing %s child assets", character, len(new_assets))
            # TODO: `ignore_conflicts=True` needed as workaround to compensate for
            # occasional duplicate FK constraint errors. Needs to be investigated
            CharacterAsset.objects.bulk_create(
                new_assets,
                batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
                ignore_conflicts=True,
            )

    if new_assets and assets_flat:
        # there are more child assets to create
        assets_create_children.apply_async(
            kwargs={
                "asset_list": list(assets_flat.values()),
                "character_pk": character.pk,
                "cycle": cycle + 1,
            },
            priority=DEFAULT_TASK_PRIORITY,
        )
    else:
        _log_character_update_success(character, Character.UpdateSection.ASSETS)
        if len(assets_flat) > 0:
            logger.warning(
                "%s: Failed to add %s assets to the tree: %s",
                character,
                len(assets_flat),
                assets_flat.keys(),
            )


# Special tasks for updating mail section


@shared_task(**TASK_ESI_KWARGS)
def update_character_mails(
    self,
    character_pk: int,
    force_update: bool = False,
    root_task_id: str = None,
    parent_task_id: str = None,
) -> None:
    """Main task for updating mails of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    section = Character.UpdateSection.MAILS
    logger.info(
        "%s: Updating %s", character, Character.UpdateSection.display_name(section)
    )
    character.reset_update_section(
        section=section, root_task_id=root_task_id, parent_task_id=parent_task_id
    )
    chain(
        update_character_mailing_lists.si(character.pk, force_update=force_update),
        update_character_mail_labels.si(character.pk, force_update=force_update),
        update_character_mail_headers.si(character.pk, force_update=force_update),
        update_character_mail_bodies.si(character.pk),
        update_unresolved_eve_entities.si(character.pk, section),
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_ESI_KWARGS)
def update_character_mailing_lists(
    self, character_pk: int, force_update: bool = False
) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.MAILS,
        character.update_mailing_lists,
        force_update=force_update,
    )


@shared_task(**TASK_ESI_KWARGS)
def update_character_mail_labels(
    self, character_pk: int, force_update: bool = False
) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.MAILS,
        character.update_mail_labels,
        force_update=force_update,
    )


@shared_task(**TASK_ESI_KWARGS)
def update_character_mail_headers(
    self, character_pk: int, force_update: bool = False
) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.MAILS,
        character.update_mail_headers,
        force_update=force_update,
    )


@shared_task(**TASK_ESI_KWARGS)
def update_mail_body_esi(self, character_pk: int, mail_pk: int):
    """Task for updating the body of a mail from ESI"""
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    mail = CharacterMail.objects.get(pk=mail_pk)
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.MAILS,
        character.update_mail_body,
        mail,
    )


@shared_task(**TASK_ESI_KWARGS)
def update_character_mail_bodies(self, character_pk: int) -> None:
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    mails_without_body_qs = character.mails.filter(body="")
    mails_without_body_count = mails_without_body_qs.count()

    if mails_without_body_count > 0:
        logger.info("%s: Loading %s mailbodies", character, mails_without_body_count)
        for mail in mails_without_body_qs:
            update_mail_body_esi.apply_async(
                kwargs={"character_pk": character.pk, "mail_pk": mail.pk},
                priority=DEFAULT_TASK_PRIORITY,
            )

    # the last task in the chain logs success (if any)
    _log_character_update_success(character, Character.UpdateSection.MAILS)


# special tasks for updating contacts


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_contacts(
    character_pk: int,
    force_update: bool = False,
    root_task_id: str = None,
    parent_task_id: str = None,
) -> None:
    """Main task for updating contacts of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    section = Character.UpdateSection.CONTACTS
    character.reset_update_section(
        section=section, root_task_id=root_task_id, parent_task_id=parent_task_id
    )
    logger.info(
        "%s: Updating %s", character, Character.UpdateSection.display_name(section)
    )
    chain(
        update_character_contact_labels.si(character.pk, force_update=force_update),
        update_character_contacts_2.si(character.pk, force_update=force_update),
        update_unresolved_eve_entities.si(character.pk, section, last_in_chain=True),
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_ESI_KWARGS)
def update_character_contact_labels(
    self, character_pk: int, force_update: bool = False
) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.CONTACTS,
        character.update_contact_labels,
        force_update=force_update,
    )


@shared_task(**TASK_ESI_KWARGS)
def update_character_contacts_2(
    self, character_pk: int, force_update: bool = False
) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.CONTACTS,
        character.update_contacts,
        force_update=force_update,
    )


# special tasks for updating contracts


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_contracts(
    character_pk: int,
    force_update: bool = False,
    root_task_id: str = None,
    parent_task_id: str = None,
) -> None:
    """Main task for updating contracts of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    section = Character.UpdateSection.CONTRACTS
    character.reset_update_section(
        section=section, root_task_id=root_task_id, parent_task_id=parent_task_id
    )
    logger.info(
        "%s: Updating %s", character, Character.UpdateSection.display_name(section)
    )
    chain(
        update_character_contract_headers.si(character.pk, force_update=force_update),
        update_character_contracts_items.si(character.pk),
        update_character_contracts_bids.si(character.pk),
        update_unresolved_eve_entities.si(character.pk, section, last_in_chain=True),
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_ESI_KWARGS)
def update_character_contract_headers(
    self, character_pk: int, force_update: bool = False
) -> bool:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.CONTRACTS,
        character.update_contract_headers,
        force_update=force_update,
    )


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_contracts_items(character_pk: int):
    """Update items for all contracts of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    contract_pks = set(
        character.contracts.filter(
            contract_type__in=[
                CharacterContract.TYPE_ITEM_EXCHANGE,
                CharacterContract.TYPE_AUCTION,
            ],
            items__isnull=True,
        ).values_list("pk", flat=True)
    )
    if len(contract_pks) > 0:
        logger.info(
            "%s: Starting updating items for %s contracts", character, len(contract_pks)
        )
        for contract_pk in contract_pks:
            update_contract_items_esi.apply_async(
                kwargs={"character_pk": character.pk, "contract_pk": contract_pk},
                priority=DEFAULT_TASK_PRIORITY,
            )

    else:
        logger.info("%s: No items to update", character)


@shared_task(**TASK_ESI_KWARGS)
def update_contract_items_esi(self, character_pk: int, contract_pk: int):
    """Task for updating the items of a contract from ESI"""
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    contract = CharacterContract.objects.get(pk=contract_pk)
    character.update_contract_items(contract)


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_contracts_bids(character_pk: int):
    """Update bids for all contracts of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    contract_pks = set(
        character.contracts.filter(
            contract_type__in=[CharacterContract.TYPE_AUCTION],
            status=CharacterContract.STATUS_OUTSTANDING,
        ).values_list("pk", flat=True)
    )
    if len(contract_pks) > 0:
        logger.info(
            "%s: Starting updating bids for %s contracts", character, len(contract_pks)
        )
        for contract_pk in contract_pks:
            update_contract_bids_esi.apply_async(
                kwargs={"character_pk": character.pk, "contract_pk": contract_pk},
                priority=DEFAULT_TASK_PRIORITY,
            )

    else:
        logger.info("%s: No bids to update", character)


@shared_task(**TASK_ESI_KWARGS)
def update_contract_bids_esi(self, character_pk: int, contract_pk: int):
    """Task for updating the bids of a contract from ESI"""
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    contract = CharacterContract.objects.get(pk=contract_pk)
    character.update_contract_bids(contract)


# special tasks for updating wallet


@shared_task(**TASK_DEFAULT_KWARGS)
def update_character_wallet_journal(
    character_pk: int, root_task_id: str = None, parent_task_id: str = None
) -> None:
    """Main task for updating wallet journal of a character"""
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    section = Character.UpdateSection.WALLET_JOURNAL
    character.reset_update_section(
        section=section, root_task_id=root_task_id, parent_task_id=parent_task_id
    )
    logger.info(
        "%s: Updating %s", character, Character.UpdateSection.display_name(section)
    )
    chain(
        update_character_wallet_journal_entries.si(character.pk),
        update_unresolved_eve_entities.si(character.pk, section, last_in_chain=True),
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_ESI_KWARGS)
def update_character_wallet_journal_entries(self, character_pk: int) -> None:
    _retry_if_esi_is_down(self)
    character = Character.objects.get_cached(
        pk=character_pk, timeout=MEMBERAUDIT_TASKS_OBJECT_CACHE_TIMEOUT
    )
    _character_update_with_error_logging(
        self,
        character,
        Character.UpdateSection.WALLET_JOURNAL,
        character.update_wallet_journal,
    )


# Tasks for other objects


@shared_task(**TASK_ESI_KWARGS)
def update_market_prices(self):
    """Update market prices from ESI"""
    _retry_if_esi_is_down(self)
    EveMarketPrice.objects.update_from_esi(
        minutes_until_stale=MEMBERAUDIT_UPDATE_STALE_RING_2
    )


@shared_task(
    **{
        **TASK_ESI_KWARGS,
        **{
            "base": QueueOnce,
            "once": {"keys": ["id"], "graceful": True},
            "max_retries": None,
        },
    },
)
def update_structure_esi(self, id: int, token_pk: int):
    """Updates a structure object from ESI
    and retries later if the ESI error limit has already been reached
    """
    try:
        token = Token.objects.get(pk=token_pk)
    except Token.DoesNotExist as ex:
        raise Token.DoesNotExist(
            f"Location #{id}: Requested token with pk {token_pk} does not exist"
        ) from ex

    try:
        Location.objects.structure_update_or_create_esi(id, token)
    except EsiOffline as ex:
        countdown = (30 + int(random.uniform(1, 20))) * 60
        logger.warning(
            "Location #%s: ESI appears to be offline. Trying again in %d minutes.",
            id,
            countdown,
        )
        raise self.retry(countdown=countdown) from ex
    except EsiErrorLimitExceeded as ex:
        logger.warning(
            "Location #%s: ESI error limit threshold reached. "
            "Trying again in %s seconds",
            id,
            ex.retry_in,
        )
        raise self.retry(countdown=ex.retry_in) from ex


@shared_task(
    **{
        **TASK_ESI_KWARGS,
        **{
            "base": QueueOnce,
            "once": {"keys": ["id"], "graceful": True},
            "max_retries": None,
        },
    },
)
def update_mail_entity_esi(self, id: int, category: str = None):
    """Updates a mail entity object from ESI
    and retries later if the ESI error limit has already been reached
    """
    try:
        MailEntity.objects.update_or_create_esi(id=id, category=category)
    except EsiOffline as ex:
        logger.warning(
            "MailEntity #%s: ESI appears to be offline. Trying again in 30 minutes.", id
        )
        raise self.retry(countdown=30 * 60 + int(random.uniform(1, 20))) from ex
    except EsiErrorLimitExceeded as ex:
        logger.warning(
            "MailEntity #%s: ESI error limit threshold reached. "
            "Trying again in %s seconds",
            id,
            ex.retry_in,
        )
        raise self.retry(countdown=ex.retry_in)


@shared_task(**TASK_DEFAULT_KWARGS)
def update_characters_skill_checks(force_update: bool = False) -> None:
    """Start the update of skill checks for all registered characters

    Args:
    - force_update: When set to True will always update regardless of stale status
    """
    section = Character.UpdateSection.SKILL_SETS
    for character in Character.objects.all():
        if force_update or character.is_update_section_stale(section):
            update_character_section.apply_async(
                kwargs={
                    "character_pk": character.pk,
                    "section": section,
                    "force_update": force_update,
                },
                priority=DEFAULT_TASK_PRIORITY,
            )


@shared_task(**TASK_DEFAULT_KWARGS)
def delete_character(character_pk) -> None:
    """Delete a member audit character"""
    character = Character.objects.get(pk=character_pk)
    logger.info("%s: Deleting character", character)
    character.delete()


@shared_task(**TASK_DEFAULT_KWARGS)
def export_data(user_pk: int = None) -> None:
    """Export data to files."""
    tasks = [
        _export_data_for_topic.si(topic) for topic in data_exporters.DataExporter.topics
    ]
    if user_pk:
        tasks.append(_export_data_inform_user.si(user_pk))
    chain(tasks).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**TASK_DEFAULT_KWARGS)
def export_data_for_topic(topic: str, user_pk: int) -> str:
    chain(
        _export_data_for_topic.si(topic), _export_data_inform_user.si(user_pk, topic)
    ).apply_async(priority=DEFAULT_TASK_PRIORITY)


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"base": QueueOnce}})
def _export_data_for_topic(topic: str, destination_folder: str = None) -> str:
    """Export data for given topic into a zipped file in destination."""
    file_path = data_exporters.export_topic_to_archive(
        topic=topic, destination_folder=destination_folder
    )
    return str(file_path)


@shared_task(**TASK_DEFAULT_KWARGS)
def _export_data_inform_user(user_pk: int, topic: str = None):
    user = User.objects.get(pk=user_pk)
    if topic:
        title = f"{__title__}: Data export for {topic} completed"
        message = f"Data export has been completed for topic {topic}."
    else:
        title = f"{__title__}: Full data export completed"
        message = (
            "Data export for all topics has been completed. "
            "It covers the following:\n"
        )
        for topic in data_exporters.DataExporter.topics:
            message += f"- {topic}\n"
    notify(user=user, title=title, message=message, level="INFO")
