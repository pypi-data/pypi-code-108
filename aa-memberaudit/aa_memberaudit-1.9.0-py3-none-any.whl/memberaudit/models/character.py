"""
Character and CharacterUpdateStatus models
"""

import datetime as dt
import hashlib
import json
import os
from typing import Any, Optional

from bravado.exception import HTTPNotFound

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from esi.errors import TokenError
from esi.models import Token
from eveuniverse.models import EveEntity, EveType

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger
from app_utils.allianceauth import notify_throttled
from app_utils.datetime import datetime_round_hour
from app_utils.helpers import chunks
from app_utils.logging import LoggerAddTag

from .. import __title__
from ..app_settings import (
    MEMBERAUDIT_APP_NAME,
    MEMBERAUDIT_DATA_RETENTION_LIMIT,
    MEMBERAUDIT_DEVELOPER_MODE,
    MEMBERAUDIT_MAX_MAILS,
    MEMBERAUDIT_UPDATE_STALE_OFFSET,
    MEMBERAUDIT_UPDATE_STALE_RING_1,
    MEMBERAUDIT_UPDATE_STALE_RING_2,
    MEMBERAUDIT_UPDATE_STALE_RING_3,
)
from ..core.xml_converter import eve_xml_to_html
from ..decorators import fetch_token_for_character
from ..managers.character import CharacterManager, CharacterUpdateStatusManager
from ..providers import esi
from .general import Location

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def data_retention_cutoff() -> Optional[dt.datetime]:
    """returns cutoff datetime for data retention of None if unlimited"""
    if MEMBERAUDIT_DATA_RETENTION_LIMIT is None:
        return None
    else:
        return datetime_round_hour(
            now() - dt.timedelta(days=MEMBERAUDIT_DATA_RETENTION_LIMIT)
        )


class Character(models.Model):
    """A character synced by this app

    This is the head model for all characters
    """

    class UpdateSection(models.TextChoices):
        ASSETS = "assets", _("assets")
        CHARACTER_DETAILS = "character_details", ("character details")
        CONTACTS = "contacts", _("contacts")
        CONTRACTS = "contracts", _("contracts")
        CORPORATION_HISTORY = "corporation_history", _("corporation history")
        IMPLANTS = "implants", _("implants")
        JUMP_CLONES = "jump_clones", _("jump clones")
        LOCATION = "location", _("location")
        LOYALTY = "loyalty", _("loyalty")
        MAILS = "mails", _("mails")
        ONLINE_STATUS = "online_status", _("online status")
        SHIP = "ship", _("ship")
        SKILLS = "skills", _("skills")
        SKILL_QUEUE = "skill_queue", _("skill queue")
        SKILL_SETS = "skill_sets", _("skill sets")
        WALLET_BALLANCE = "wallet_balance", _("wallet balance")
        WALLET_JOURNAL = "wallet_journal", _("wallet journal")
        WALLET_TRANSACTIONS = "wallet_transactions", _("wallet transactions")
        ATTRIBUTES = "attributes", _("attributes")

        @classmethod
        def method_name(cls, section: str) -> str:
            """returns name of update method corresponding with the given section

            Raises:
            - ValueError if secton is invalid
            """
            if section not in cls.values:
                raise ValueError(f"Unknown section: {section}")

            return f"update_{section}"

        @classmethod
        def display_name(cls, section: str) -> str:
            """returns display name of given section

            Raises:
            - ValueError if secton is invalid
            """
            for short_name, long_name in cls.choices:
                if short_name == section:
                    return long_name

            raise ValueError(f"Unknown section: {section}")

    UPDATE_SECTION_RINGS_MAP = {
        UpdateSection.ASSETS: 3,
        UpdateSection.CHARACTER_DETAILS: 2,
        UpdateSection.CONTACTS: 2,
        UpdateSection.CONTRACTS: 2,
        UpdateSection.CORPORATION_HISTORY: 2,
        UpdateSection.SKILL_SETS: 2,
        UpdateSection.IMPLANTS: 2,
        UpdateSection.JUMP_CLONES: 2,
        UpdateSection.LOCATION: 1,
        UpdateSection.LOYALTY: 2,
        UpdateSection.MAILS: 2,
        UpdateSection.ONLINE_STATUS: 1,
        UpdateSection.SHIP: 1,
        UpdateSection.SKILLS: 2,
        UpdateSection.SKILL_QUEUE: 1,
        UpdateSection.WALLET_BALLANCE: 2,
        UpdateSection.WALLET_JOURNAL: 2,
        UpdateSection.WALLET_TRANSACTIONS: 2,
        UpdateSection.ATTRIBUTES: 3,
    }

    character_ownership = models.OneToOneField(
        CharacterOwnership,
        related_name="memberaudit_character",
        on_delete=models.CASCADE,
        primary_key=True,
        help_text="ownership of this character on Auth",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_shared = models.BooleanField(
        default=False,
        help_text="Shared characters can be viewed by recruiters",
    )
    mailing_lists = models.ManyToManyField("MailEntity", related_name="characters")

    objects = CharacterManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f"{self.character_ownership.character.character_name} (PK:{self.pk})"

    def __repr__(self) -> str:
        return (
            f"Character(pk={self.pk}, "
            f"character_ownership='{self.character_ownership}')"
        )

    @cached_property
    def is_main(self) -> bool:
        """returns True if this character is a main character, else False"""
        try:
            return (
                self.character_ownership.user.profile.main_character.character_id
                == self.character_ownership.character.character_id
            )
        except AttributeError:
            return False

    @cached_property
    def name(self) -> str:
        return self.character_ownership.character.character_name

    def user_is_owner(self, user: User) -> bool:
        """Return True if the given user is owner of this character"""
        return self.character_ownership.user == user

    def user_has_access(self, user: User) -> bool:
        """Returns True if given user has permission to access this character
        in the character viewer
        """
        if self.character_ownership.user == user:  # shortcut for better performance
            return True
        return Character.objects.user_has_access(user).filter(pk=self.pk).exists()

    def is_update_status_ok(self) -> bool:
        """returns status of last update

        Returns:
        - True: If update was complete and without errors
        - False if there where any errors
        - None: if last update is incomplete
        """
        errors_count = self.update_status_set.filter(is_success=False).count()
        ok_count = self.update_status_set.filter(is_success=True).count()
        if errors_count > 0:
            return False
        elif ok_count == len(Character.UpdateSection.choices):
            return True
        else:
            return None

    @classmethod
    def update_section_time_until_stale(cls, section: str) -> dt.timedelta:
        """time until given update section is considered stale"""
        ring = cls.UPDATE_SECTION_RINGS_MAP[section]
        if ring == 1:
            minutes = MEMBERAUDIT_UPDATE_STALE_RING_1
        elif ring == 2:
            minutes = MEMBERAUDIT_UPDATE_STALE_RING_2
        else:
            minutes = MEMBERAUDIT_UPDATE_STALE_RING_3

        # setting reduced by offset to ensure all sections are stale when
        # periodic task starts
        return dt.timedelta(minutes=minutes - MEMBERAUDIT_UPDATE_STALE_OFFSET)

    @classmethod
    def sections_in_ring(cls, ring: int) -> set:
        """returns set of sections for given ring"""
        return {
            section
            for section, ring_num in cls.UPDATE_SECTION_RINGS_MAP.items()
            if ring_num == ring
        }

    def is_update_section_stale(self, section: str) -> bool:
        """returns True if the give update section is stale, else False"""
        try:
            update_status = self.update_status_set.get(
                section=section,
                is_success=True,
                started_at__isnull=False,
                finished_at__isnull=False,
            )
        except (CharacterUpdateStatus.DoesNotExist, ObjectDoesNotExist, AttributeError):
            return True

        deadline = now() - self.update_section_time_until_stale(section)
        return update_status.started_at < deadline

    def has_section_changed(
        self, section: str, content: str, hash_num: int = 1
    ) -> bool:
        """returns False if the content hash for this section has not changed, else True"""
        try:
            section = self.update_status_set.get(section=section)
        except CharacterUpdateStatus.DoesNotExist:
            return True
        else:
            return section.has_changed(content=content, hash_num=hash_num)

    def update_section_content_hash(
        self, section: str, content: str, hash_num: int = 1
    ) -> bool:
        try:
            section = self.update_status_set.get(section=section)
        except CharacterUpdateStatus.DoesNotExist:
            section, _ = CharacterUpdateStatus.objects.get_or_create(
                character=self, section=section
            )

        section.update_content_hash(content=content, hash_num=hash_num)

    def reset_update_section(
        self, section: str, root_task_id: str = None, parent_task_id: str = None
    ) -> "CharacterUpdateStatus":
        """resets status of given update section and returns it"""
        try:
            section = self.update_status_set.get(section=section)
        except CharacterUpdateStatus.DoesNotExist:
            section, _ = CharacterUpdateStatus.objects.get_or_create(
                character=self, section=section
            )

        section.reset(root_task_id, parent_task_id)
        return section

    def is_section_updating(self, section: str) -> bool:
        """returns True if section is currently updating, or does not exist, else False"""
        try:
            section = self.update_status_set.get(section=section)
        except CharacterUpdateStatus.DoesNotExist:
            return True

        return section.is_updating

    def _preload_all_locations(self, token: Token, incoming_ids: set) -> list:
        """loads location objects specified by given set

        returns list of existing location IDs after preload
        """
        existing_ids = set(Location.objects.values_list("id", flat=True))
        missing_ids = incoming_ids.difference(existing_ids)
        if missing_ids:
            logger.info(
                "%s: Loading %s missing locations from ESI", self, len(missing_ids)
            )
            for location_id in missing_ids:
                try:
                    Location.objects.get_or_create_esi_async(
                        id=location_id, token=token
                    )
                except ValueError:
                    pass
                else:
                    existing_ids.add(location_id)

        return existing_ids

    def fetch_token(self, scopes=None) -> Token:
        """returns valid token for character

        Args:
        - scopes: Optionally provide the required scopes.
        Otherwise will use all scopes defined for this character.

        Exceptions:
        - TokenError: If no valid token can be found
        """
        user = self.character_ownership.user
        character = self.character_ownership.character
        token = (
            Token.objects.prefetch_related("scopes")
            .filter(user=user, character_id=character.character_id)
            .require_scopes(scopes if scopes else self.get_esi_scopes())
            .require_valid()
            .first()
        )
        if not token:
            message_id = f"{__title__}-fetch_token-{self.pk}-TokenError"
            title = f"{__title__}: Invalid or missing token for {character}"
            message = (
                f"{MEMBERAUDIT_APP_NAME} could not find a valid token for your "
                f"character {character}.\n"
                f"Please re-add that character to {MEMBERAUDIT_APP_NAME} "
                "at your earliest convenience to update your token."
            )
            notify_throttled(
                message_id=message_id, user=user, title=title, message=message
            )
            raise TokenError(f"Could not find a matching token for {self}")

        return token

    @fetch_token_for_character("esi-assets.read_assets.v1")
    def assets_build_list_from_esi(
        self, token: Token, force_update=False
    ) -> Optional[list]:
        """fetches assets from ESI and preloads related objects from ESI

        returns the asset_list or None if no update is required
        """
        logger.info("%s: Fetching assets from ESI", self)
        asset_list = esi.client.Assets.get_characters_character_id_assets(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        assets_flat = {int(x["item_id"]): x for x in asset_list}

        logger.info("%s: Fetching asset names from ESI", self)
        names = list()
        for asset_ids_chunk in chunks(list(assets_flat.keys()), 999):
            names += esi.client.Assets.post_characters_character_id_assets_names(
                character_id=self.character_ownership.character.character_id,
                token=token.valid_access_token(),
                item_ids=asset_ids_chunk,
            ).results()

        asset_names = {
            int(x["item_id"]): x["name"] for x in names if x["name"] != "None"
        }
        for item_id in assets_flat.keys():
            assets_flat[item_id]["name"] = asset_names.get(item_id, "")

        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(assets_flat, "asset_list")

        new_asset_list = list(assets_flat.values())
        if force_update or self.has_section_changed(
            section=Character.UpdateSection.ASSETS, content=new_asset_list
        ):
            self.update_section_content_hash(
                section=Character.UpdateSection.ASSETS, content=new_asset_list
            )
            return new_asset_list
        else:
            logger.info("%s: Assets did not change", self)
            return None

    @fetch_token_for_character("esi-universe.read_structures.v1")
    def assets_preload_objects(self, token: Token, asset_list: list) -> None:
        """preloads objects needed to build the asset tree"""
        logger.info("%s: Preloading objects for asset tree", self)
        required_ids = {x["type_id"] for x in asset_list if "type_id" in x}
        existing_ids = set(EveType.objects.values_list("id", flat=True))
        missing_ids = required_ids.difference(existing_ids)
        if missing_ids:
            logger.info("%s: Loading %s missing types from ESI", self, len(missing_ids))
            EveType.objects.bulk_get_or_create_esi(ids=missing_ids)

        assets_flat = {int(x["item_id"]): x for x in asset_list}
        incoming_location_ids = {
            x["location_id"]
            for x in assets_flat.values()
            if "location_id" in x and x["location_id"] not in assets_flat
        }
        self._preload_all_locations(token=token, incoming_ids=incoming_location_ids)

    def update_character_details(self, force_update: bool = False):
        """syncs the character details for the given character"""
        from .sections import CharacterDetails

        logger.info("%s: Fetching character details from ESI", self)
        details = esi.client.Character.get_characters_character_id(
            character_id=self.character_ownership.character.character_id,
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(details, "character_details")

        if force_update or self.has_section_changed(
            section=self.UpdateSection.CHARACTER_DETAILS, content=details
        ):
            CharacterDetails.objects.update_for_character(self, details)
            self.update_section_content_hash(
                section=self.UpdateSection.CHARACTER_DETAILS, content=details
            )

        else:
            logger.info("%s: Character details have not changed", self)

    @fetch_token_for_character("esi-characters.read_contacts.v1")
    def update_contact_labels(self, token: Token, force_update: bool = False):
        logger.info("%s: Fetching contact labels from ESI", self)
        labels = esi.client.Contacts.get_characters_character_id_contacts_labels(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(labels, "contact_labels")
        if force_update or self.has_section_changed(
            section=self.UpdateSection.CONTACTS, content=labels, hash_num=2
        ):
            self.contact_labels.update_for_character(self, labels)
            self.update_section_content_hash(
                section=self.UpdateSection.CONTACTS, content=labels, hash_num=2
            )
        else:
            logger.info("%s: Contact labels have not changed", self)

    @fetch_token_for_character("esi-characters.read_contacts.v1")
    def update_contacts(self, token: Token, force_update: bool = False):
        logger.info("%s: Fetching contacts from ESI", self)
        contacts_data = esi.client.Contacts.get_characters_character_id_contacts(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(contacts_data, "contacts")
        if contacts_data:
            contacts_list = {int(x["contact_id"]): x for x in contacts_data}
        else:
            contacts_list = dict()
        if force_update or self.has_section_changed(
            section=self.UpdateSection.CONTACTS, content=contacts_list
        ):
            self.contacts.update_for_character(self, contacts_list)
            self.update_section_content_hash(
                section=self.UpdateSection.CONTACTS, content=contacts_list
            )
        else:
            logger.info("%s: Contacts have not changed", self)

    @fetch_token_for_character("esi-contracts.read_character_contracts.v1")
    def update_contract_headers(self, token: Token, force_update: bool = False):
        """update the character's contract headers"""
        contracts_list = self._fetch_contracts_from_esi(token)
        if not contracts_list:
            logger.info("%s: No contracts received from ESI", self)
        cutoff_datetime = data_retention_cutoff()
        if cutoff_datetime:
            self.contracts.filter(date_expired__lt=cutoff_datetime).delete()
        if force_update or self.has_section_changed(
            section=self.UpdateSection.CONTRACTS, content=contracts_list
        ):
            existing_ids = set(self.contracts.values_list("contract_id", flat=True))
            incoming_location_ids = {
                obj["start_location_id"]
                for contract_id, obj in contracts_list.items()
                if contract_id not in existing_ids
            }
            incoming_location_ids |= {
                obj["end_location_id"] for obj in contracts_list.values()
            }
            self._preload_all_locations(token=token, incoming_ids=incoming_location_ids)
            self.contracts.update_for_character(self, contracts_list)
            self.update_section_content_hash(
                section=self.UpdateSection.CONTRACTS, content=contracts_list
            )
        else:
            logger.info("%s: Contracts have not changed", self)

    def _fetch_contracts_from_esi(self, token) -> dict:
        logger.info("%s: Fetching contracts from ESI", self)
        contracts_data = esi.client.Contracts.get_characters_character_id_contracts(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(contracts_data, "contracts")

        cutoff_datetime = data_retention_cutoff()
        contracts_list = {
            obj.get("contract_id"): obj
            for obj in contracts_data
            if cutoff_datetime is None or obj.get("date_expired") > cutoff_datetime
        }
        return contracts_list

    @fetch_token_for_character("esi-contracts.read_character_contracts.v1")
    def update_contract_items(self, token: Token, contract: models.Model):
        """update the character's contract details"""
        if contract.contract_type not in [
            contract.TYPE_ITEM_EXCHANGE,
            contract.TYPE_AUCTION,
        ]:
            logger.warning(
                "%s, %s: Can not update items. Wrong contract type.",
                self,
                contract.contract_id,
            )
            return

        logger.info(
            "%s, %s: Fetching contract items from ESI", self, contract.contract_id
        )
        my_esi = esi.client.Contracts
        items_data = my_esi.get_characters_character_id_contracts_contract_id_items(
            character_id=self.character_ownership.character.character_id,
            contract_id=contract.contract_id,
            token=token.valid_access_token(),
        ).results()
        contract.items.update_for_contract(contract, items_data)

    @fetch_token_for_character("esi-contracts.read_character_contracts.v1")
    def update_contract_bids(self, token: Token, contract: models.Model):
        """update the character's contract details"""
        if contract.contract_type != contract.TYPE_AUCTION:
            logger.warning(
                "%s, %s: Can not update bids. Wrong contract type.",
                self,
                contract.contract_id,
            )
            return

        logger.info(
            "%s, %s: Fetching contract bids from ESI", self, contract.contract_id
        )
        bids_data = (
            esi.client.Contracts.get_characters_character_id_contracts_contract_id_bids(
                character_id=self.character_ownership.character.character_id,
                contract_id=contract.contract_id,
                token=token.valid_access_token(),
            ).results()
        )
        bids_list = {int(x["bid_id"]): x for x in bids_data if "bid_id" in x}
        contract.bids.update_for_contract(contract, bids_list)
        EveEntity.objects.bulk_update_new_esi()

    def update_corporation_history(self, force_update: bool = False):
        """syncs the character's corporation history"""
        logger.info("%s: Fetching corporation history from ESI", self)
        history = esi.client.Character.get_characters_character_id_corporationhistory(
            character_id=self.character_ownership.character.character_id,
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(history, "corporation_history")
        if force_update or self.has_section_changed(
            section=self.UpdateSection.CORPORATION_HISTORY, content=history
        ):
            self.corporation_history.update_for_character(self, history)
            self.update_section_content_hash(
                section=self.UpdateSection.CORPORATION_HISTORY, content=history
            )
        else:
            logger.info("%s: Corporation history has not changed", self)

    @fetch_token_for_character("esi-clones.read_implants.v1")
    def update_implants(self, token: Token, force_update: bool = False):
        """update the character's implants"""
        logger.info("%s: Fetching implants from ESI", self)
        implants_data = esi.client.Clones.get_characters_character_id_implants(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(implants_data, "implants")
        if force_update or self.has_section_changed(
            section=self.UpdateSection.IMPLANTS, content=implants_data
        ):
            if implants_data:
                EveType.objects.bulk_get_or_create_esi(ids=implants_data)
            self.implants.update_for_character(self, implants_data)
            self.update_section_content_hash(
                section=self.UpdateSection.IMPLANTS, content=implants_data
            )
        else:
            logger.info("%s: Implants have not changed", self)

    @fetch_token_for_character(
        ["esi-location.read_location.v1", "esi-universe.read_structures.v1"]
    )
    def update_location(self, token: Token):
        """update the location for the given character"""
        from .sections import CharacterLocation

        logger.info("%s: Fetching location from ESI", self)
        location_info = esi.client.Location.get_characters_character_id_location(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        CharacterLocation.objects.update_for_character(self, token, location_info)

    @fetch_token_for_character("esi-characters.read_loyalty.v1")
    def update_loyalty(self, token: Token, force_update: bool = False):
        """syncs the character's loyalty entries"""
        logger.info("%s: Fetching loyalty entries from ESI", self)
        loyalty_entries = esi.client.Loyalty.get_characters_character_id_loyalty_points(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(loyalty_entries, "loyalty")

        if force_update or self.has_section_changed(
            section=self.UpdateSection.LOYALTY, content=loyalty_entries
        ):
            self.loyalty_entries.update_for_character(self, loyalty_entries)
            self.update_section_content_hash(
                section=self.UpdateSection.LOYALTY, content=loyalty_entries
            )
            EveEntity.objects.bulk_update_new_esi()

        else:
            logger.info("%s: Loyalty entries have not changed", self)

    @fetch_token_for_character(
        ["esi-clones.read_clones.v1", "esi-universe.read_structures.v1"]
    )
    def update_jump_clones(self, token: Token, force_update: bool = False):
        """updates the character's jump clones"""
        logger.info("%s: Fetching jump clones from ESI", self)
        jump_clones_info = esi.client.Clones.get_characters_character_id_clones(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(jump_clones_info, "jump_clones")

        if force_update or self.has_section_changed(
            section=self.UpdateSection.JUMP_CLONES, content=jump_clones_info
        ):
            jump_clones_list = jump_clones_info.get("jump_clones")
            # fetch related objects ahead of transaction
            if jump_clones_list:
                incoming_location_ids = {
                    record["location_id"]
                    for record in jump_clones_info["jump_clones"]
                    if "location_id" in record
                }
                self._preload_all_locations(token, incoming_location_ids)

                for jump_clone_info in jump_clones_list:
                    if jump_clone_info.get("implants"):
                        EveType.objects.bulk_get_or_create_esi(
                            ids=jump_clone_info.get("implants", [])
                        )

            self.jump_clones.update_for_character(self, jump_clones_list)
            self.update_section_content_hash(
                section=self.UpdateSection.JUMP_CLONES, content=jump_clones_info
            )

        else:
            logger.info("%s: Jump clones have not changed", self)

    @fetch_token_for_character("esi-mail.read_mail.v1")
    def update_mailing_lists(self, token: Token, force_update: bool = False):
        """update mailing lists with input from given character

        Note: Obsolete mailing lists must not be removed,
        since they might still be referenced by older mails
        """
        logger.info("%s: Fetching mailing lists from ESI", self)
        mailing_lists_raw = esi.client.Mail.get_characters_character_id_mail_lists(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if mailing_lists_raw:
            mailing_lists = {
                obj["mailing_list_id"]: obj
                for obj in mailing_lists_raw
                if "mailing_list_id" in obj
            }
        else:
            mailing_lists = dict()

        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(mailing_lists, "mailing_lists")

        # TODO: replace with bulk methods to optimize

        incoming_ids = set(mailing_lists.keys())
        # existing_ids = set(self.mailing_lists.values_list("list_id", flat=True))
        if not incoming_ids:
            logger.info("%s: No new mailing lists", self)
            return

        if force_update or self.has_section_changed(
            section=self.UpdateSection.MAILS, content=mailing_lists, hash_num=2
        ):
            new_mailing_lists = self.mailing_lists.update_for_character(
                character=self, mailing_lists=mailing_lists
            )
            self.mailing_lists.set(new_mailing_lists, clear=True)
            self.update_section_content_hash(
                section=self.UpdateSection.MAILS, content=mailing_lists, hash_num=2
            )

        else:
            logger.info("%s: Mailng lists have not changed", self)

    @fetch_token_for_character("esi-mail.read_mail.v1")
    def update_mail_labels(self, token: Token, force_update: bool = False):
        """update the mail lables for the given character"""
        mail_labels_list = self._fetch_mail_labels_from_esi(token)
        if not mail_labels_list:
            logger.info("%s: No mail labels", self)
            return

        if force_update or self.has_section_changed(
            section=self.UpdateSection.MAILS, content=mail_labels_list, hash_num=3
        ):
            self.mail_labels.update_for_character(self, mail_labels_list)
            self.update_section_content_hash(
                section=self.UpdateSection.MAILS, content=mail_labels_list, hash_num=3
            )

        else:
            logger.info("%s: Mail labels have not changed", self)

    def _fetch_mail_labels_from_esi(self, token) -> dict:
        from .sections import CharacterMailUnreadCount

        logger.info("%s: Fetching mail labels from ESI", self)
        mail_labels_info = esi.client.Mail.get_characters_character_id_mail_labels(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(mail_labels_info, "mail_labels")

        if mail_labels_info.get("total_unread_count"):
            CharacterMailUnreadCount.objects.update_or_create(
                character=self,
                defaults={"total": mail_labels_info.get("total_unread_count")},
            )

        mail_labels = mail_labels_info.get("labels")
        if mail_labels:
            return {obj["label_id"]: obj for obj in mail_labels if "label_id" in obj}
        else:
            return dict()

    @fetch_token_for_character("esi-mail.read_mail.v1")
    def update_mail_headers(self, token: Token, force_update: bool = False):
        mail_headers = self._fetch_mail_headers(token)
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(mail_headers, "mail_headers")
        self.mails.update_for_character(
            character=self,
            cutoff_datetime=data_retention_cutoff(),
            mail_headers=mail_headers,
            force_update=force_update,
        )

    def _fetch_mail_headers(self, token) -> dict:
        last_mail_id = None
        mail_headers_all = list()
        page = 1
        while True:
            logger.info("%s: Fetching mail headers from ESI - page %s", self, page)
            mail_headers = esi.client.Mail.get_characters_character_id_mail(
                character_id=self.character_ownership.character.character_id,
                last_mail_id=last_mail_id,
                token=token.valid_access_token(),
            ).results()
            if MEMBERAUDIT_DEVELOPER_MODE:
                self._store_list_to_disk(mail_headers, "mail_headers")

            mail_headers_all += mail_headers
            if len(mail_headers) < 50 or len(mail_headers_all) >= MEMBERAUDIT_MAX_MAILS:
                break
            else:
                last_mail_id = min([x["mail_id"] for x in mail_headers])
                page += 1

        cutoff_datetime = data_retention_cutoff()
        mail_headers_all_2 = {
            obj["mail_id"]: obj
            for obj in mail_headers_all
            if cutoff_datetime is None
            or not obj.get("timestamp")
            or obj.get("timestamp") > cutoff_datetime
        }
        logger.info(
            "%s: Received %s mail headers from ESI", self, len(mail_headers_all_2)
        )
        return mail_headers_all_2

    @staticmethod
    def _headers_list_subset(mail_headers, subset_ids) -> dict:
        return {
            mail_info["mail_id"]: mail_info
            for mail_id, mail_info in mail_headers.items()
            if mail_id in subset_ids
        }

    @fetch_token_for_character("esi-mail.read_mail.v1")
    def update_mail_body(self, token: Token, mail: models.Model) -> None:
        logger.debug("%s: Fetching body from ESI for mail ID %s", self, mail.mail_id)
        try:
            mail_body = esi.client.Mail.get_characters_character_id_mail_mail_id(
                character_id=self.character_ownership.character.character_id,
                mail_id=mail.mail_id,
                token=token.valid_access_token(),
            ).result()
        except HTTPNotFound:
            logger.info(
                "%s: Mail %s was deleted in game. Removing mail header.", self, mail
            )
            mail.delete()
            return
        mail.body = mail_body.get("body", "")
        mail.save()
        eve_xml_to_html(mail.body)  # resolve names early
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(mail_body, "mail_body")

    @fetch_token_for_character("esi-location.read_online.v1")
    def update_online_status(self, token):
        """Update the character's online status"""
        from .sections import CharacterOnlineStatus

        logger.info("%s: Fetching online status from ESI", self)
        online_info = esi.client.Location.get_characters_character_id_online(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        CharacterOnlineStatus.objects.update_or_create(
            character=self,
            defaults={
                "last_login": online_info.get("last_login"),
                "last_logout": online_info.get("last_logout"),
                "logins": online_info.get("logins"),
            },
        )

    @fetch_token_for_character("esi-location.read_ship_type.v1")
    def update_ship(self, token: Token):
        """Update the ship for the given character."""
        from .sections import CharacterShip

        logger.info("%s: Fetching ship from ESI", self)
        ship_info = esi.client.Location.get_characters_character_id_ship(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        CharacterShip.objects.update_for_character(self, ship_info)

    @fetch_token_for_character("esi-skills.read_skillqueue.v1")
    def update_skill_queue(self, token: Token, force_update: bool = False):
        """update the character's skill queue"""
        logger.info("%s: Fetching skill queue from ESI", self)
        skillqueue = esi.client.Skills.get_characters_character_id_skillqueue(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(skillqueue, "skill_queue")

        if force_update or self.has_section_changed(
            section=self.UpdateSection.SKILL_QUEUE, content=skillqueue
        ):
            self.skillqueue.update_for_character(self, skillqueue)
            self.update_section_content_hash(
                section=self.UpdateSection.SKILL_QUEUE, content=skillqueue
            )

        else:
            logger.info("%s: Skill queue has not changed", self)

    def update_skill_sets(self):
        """Checks if character has the skills needed for skill sets
        and updates results in database
        """
        self.skill_set_checks.update_for_character(self)

    @fetch_token_for_character("esi-skills.read_skills.v1")
    def update_skills(self, token, force_update: bool = False):
        """update the character's skill"""
        skills_list = self._fetch_skills_from_esi(token)
        if force_update or self.has_section_changed(
            section=self.UpdateSection.SKILLS, content=skills_list
        ):
            self._preload_types(skills_list)
            self.skills.update_for_character(self, skills_list)
            self.update_section_content_hash(
                section=self.UpdateSection.SKILLS, content=skills_list
            )

        else:
            logger.info("%s: Skills have not changed", self)

    def _fetch_skills_from_esi(self, token: Token) -> dict:
        from .sections import CharacterSkillpoints

        logger.info("%s: Fetching skills from ESI", self)
        skills_info = esi.client.Skills.get_characters_character_id_skills(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(skills_info, "skills")

        CharacterSkillpoints.objects.update_or_create(
            character=self,
            defaults={
                "total": skills_info.get("total_sp"),
                "unallocated": skills_info.get("unallocated_sp"),
            },
        )
        if skills_info.get("skills"):
            skills_list = {
                obj["skill_id"]: obj
                for obj in skills_info.get("skills")
                if "skill_id" in obj
            }
        else:
            skills_list = dict()

        return skills_list

    def _preload_types(self, skills_list: dict):
        if skills_list:
            incoming_ids = set(skills_list.keys())
            existing_ids = set(self.skills.values_list("eve_type_id", flat=True))
            new_ids = incoming_ids.difference(existing_ids)
            EveType.objects.bulk_get_or_create_esi(ids=new_ids)

    @fetch_token_for_character("esi-wallet.read_character_wallet.v1")
    def update_wallet_balance(self, token):
        """syncs the character's wallet balance"""
        from .sections import CharacterWalletBalance

        logger.info("%s: Fetching wallet balance from ESI", self)
        balance = esi.client.Wallet.get_characters_character_id_wallet(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(balance, "balance")

        CharacterWalletBalance.objects.update_or_create(
            character=self, defaults={"total": balance}
        )

    @fetch_token_for_character("esi-wallet.read_character_wallet.v1")
    def update_wallet_journal(self, token: Token) -> None:
        """syncs the character's wallet journal

        Note: Does not update unknown EvEntities.
        """
        logger.info("%s: Fetching wallet journal from ESI", self)
        journal = esi.client.Wallet.get_characters_character_id_wallet_journal(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(journal, "wallet_journal")

        self.wallet_journal.update_for_character(
            character=self, cutoff_datetime=data_retention_cutoff(), journal=journal
        )

    @fetch_token_for_character("esi-wallet.read_character_wallet.v1")
    def update_wallet_transactions(self, token):
        """syncs the character's wallet transactions"""
        logger.info("%s: Fetching wallet transactions from ESI", self)
        transactions = (
            esi.client.Wallet.get_characters_character_id_wallet_transactions(
                character_id=self.character_ownership.character.character_id,
                token=token.valid_access_token(),
            ).results()
        )
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(transactions, "wallet_transactions")
        self.wallet_transactions.update_for_character(
            character=self,
            cutoff_datetime=data_retention_cutoff(),
            transactions=transactions,
            token=token,
        )

    def _store_list_to_disk(self, lst: list, name: str):
        """stores the given list as JSON file to disk. For debugging

        Will store under memberaudit_logs/{DATE}/{CHARACTER_PK}_{NAME}.json
        """
        today_str = now().strftime("%Y%m%d")
        now_str = now().strftime("%Y%m%d%H%M")
        path = f"memberaudit_log/{today_str}"
        if not os.path.isdir(path):
            os.makedirs(path)

        fullpath = os.path.join(path, f"character_{self.pk}_{name}_{now_str}.json")
        try:
            with open(fullpath, "w", encoding="utf-8") as f:
                json.dump(lst, f, cls=DjangoJSONEncoder, sort_keys=True, indent=4)

        except OSError:
            pass

    @classmethod
    def get_esi_scopes(cls) -> list:
        return [
            "esi-assets.read_assets.v1",
            "esi-bookmarks.read_character_bookmarks.v1",
            "esi-calendar.read_calendar_events.v1",
            "esi-characters.read_agents_research.v1",
            "esi-characters.read_blueprints.v1",
            "esi-characters.read_contacts.v1",
            "esi-characters.read_fatigue.v1",
            "esi-characters.read_fw_stats.v1",
            "esi-characters.read_loyalty.v1",
            "esi-characters.read_medals.v1",
            "esi-characters.read_notifications.v1",
            "esi-characters.read_opportunities.v1",
            "esi-characters.read_standings.v1",
            "esi-characters.read_titles.v1",
            "esi-clones.read_clones.v1",
            "esi-clones.read_implants.v1",
            "esi-contracts.read_character_contracts.v1",
            "esi-corporations.read_corporation_membership.v1",
            "esi-industry.read_character_jobs.v1",
            "esi-industry.read_character_mining.v1",
            "esi-killmails.read_killmails.v1",
            "esi-location.read_location.v1",
            "esi-location.read_online.v1",
            "esi-location.read_ship_type.v1",
            "esi-mail.organize_mail.v1",
            "esi-mail.read_mail.v1",
            "esi-markets.read_character_orders.v1",
            "esi-markets.structure_markets.v1",
            "esi-planets.manage_planets.v1",
            "esi-planets.read_customs_offices.v1",
            "esi-search.search_structures.v1",
            "esi-skills.read_skillqueue.v1",
            "esi-skills.read_skills.v1",
            "esi-universe.read_structures.v1",
            "esi-wallet.read_character_wallet.v1",
        ]

    @fetch_token_for_character("esi-skills.read_skills.v1")
    def update_attributes(self, token: Token, force_update: bool = False):
        """update the character's attributes"""
        logger.info("%s: Fetching attributes from ESI", self)
        from .sections import CharacterAttributes

        attribute_data = esi.client.Skills.get_characters_character_id_attributes(
            character_id=self.character_ownership.character.character_id,
            token=token.valid_access_token(),
        ).results()
        if MEMBERAUDIT_DEVELOPER_MODE:
            self._store_list_to_disk(attribute_data, "attributes")

        if force_update or self.has_section_changed(
            section=self.UpdateSection.ATTRIBUTES, content=attribute_data
        ):
            CharacterAttributes.objects.update_for_character(self, attribute_data)
        else:
            logger.info("%s: Attributes have not changed", self)


class CharacterUpdateStatus(models.Model):
    """Update status for a character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="update_status_set"
    )

    section = models.CharField(
        max_length=64, choices=Character.UpdateSection.choices, db_index=True
    )
    is_success = models.BooleanField(
        null=True,
        default=None,
        db_index=True,
    )
    content_hash_1 = models.CharField(max_length=32, default="")
    content_hash_2 = models.CharField(max_length=32, default="")
    content_hash_3 = models.CharField(max_length=32, default="")
    last_error_message = models.TextField()
    root_task_id = models.CharField(
        max_length=36,
        default="",
        db_index=True,
        help_text="ID of update_all_characters task that started this update",
    )
    parent_task_id = models.CharField(
        max_length=36,
        default="",
        db_index=True,
        help_text="ID of character_update task that started this update",
    )
    started_at = models.DateTimeField(null=True, default=None, db_index=True)
    finished_at = models.DateTimeField(null=True, default=None, db_index=True)

    objects = CharacterUpdateStatusManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "section"],
                name="functional_pk_charactersyncstatus",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.section}"

    @property
    def is_updating(self) -> bool:
        if not self.started_at and not self.finished_at:
            return False
        else:
            return self.started_at is not None and self.finished_at is None

    def has_changed(self, content: Any, hash_num: int = 1) -> bool:
        """returns True if given content is not the same as previous one, else False"""
        new_hash = self._calculate_hash(content)
        if hash_num == 2:
            content_hash = self.content_hash_2
        elif hash_num == 3:
            content_hash = self.content_hash_3
        else:
            content_hash = self.content_hash_1

        return new_hash != content_hash

    def update_content_hash(self, content: Any, hash_num: int = 1):
        new_hash = self._calculate_hash(content)
        if hash_num == 2:
            self.content_hash_2 = new_hash
        elif hash_num == 3:
            self.content_hash_3 = new_hash
        else:
            self.content_hash_1 = new_hash

        self.save()

    @staticmethod
    def _calculate_hash(content: Any) -> str:
        return hashlib.md5(
            json.dumps(content, cls=DjangoJSONEncoder).encode("utf-8")
        ).hexdigest()

    def reset(self, root_task_id: str = None, parent_task_id: str = None) -> None:
        """resets this update status"""
        self.is_success = None
        self.last_error_message = ""
        self.started_at = now()
        self.finished_at = None
        self.root_task_id = root_task_id if root_task_id else ""
        self.parent_task_id = parent_task_id if root_task_id else ""
        self.save()
