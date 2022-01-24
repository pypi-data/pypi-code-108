import datetime as dt
from typing import Dict, List

from django.db import models, transaction
from django.db.models import Case, ExpressionWrapper, F, Value, When
from esi.models import Token
from eveuniverse.models import (
    EveAncestry,
    EveBloodline,
    EveEntity,
    EveFaction,
    EveRace,
    EveSolarSystem,
    EveType,
)

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from .. import __title__
from ..app_settings import MEMBERAUDIT_BULK_METHODS_BATCH_SIZE
from ..core.xml_converter import eve_xml_to_html
from ..helpers import get_or_create_esi_or_none, get_or_create_or_none, get_or_none

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class CharacterAssetManager(models.Manager):
    def annotate_pricing(self) -> models.QuerySet:
        """Returns qs with annotated price and total columns"""
        return (
            self.select_related("eve_type__market_price")
            .annotate(
                price=Case(
                    When(
                        is_blueprint_copy=True,
                        then=Value(None),
                    ),
                    default=F("eve_type__market_price__average_price"),
                )
            )
            .annotate(
                total=Case(
                    When(
                        is_blueprint_copy=True,
                        then=Value(None),
                    ),
                    default=ExpressionWrapper(
                        F("eve_type__market_price__average_price") * F("quantity"),
                        output_field=models.FloatField(),
                    ),
                )
            )
        )


class CharacterContactLabelManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, labels):
        # TODO: replace with bulk methods to optimize
        if labels:
            incoming_ids = {x["label_id"] for x in labels}
        else:
            incoming_ids = set()
        existing_ids = set(
            self.filter(character=character).values_list("label_id", flat=True)
        )
        obsolete_ids = existing_ids.difference(incoming_ids)
        if obsolete_ids:
            logger.info("%s: Removing %s obsolete skills", character, len(obsolete_ids))
            self.filter(character=character, label_id__in=obsolete_ids).delete()
        if incoming_ids:
            logger.info("%s: Storing %s contact labels", character, len(incoming_ids))
            for label in labels:
                self.update_or_create(
                    character=character,
                    label_id=label.get("label_id"),
                    defaults={
                        "name": label.get("label_name"),
                    },
                )
        else:
            logger.info("%s: No contact labels", character)


class CharacterContactManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, contacts_list):
        incoming_ids = set(contacts_list.keys())
        existing_ids = set(
            self.filter(character=character).values_list("eve_entity_id", flat=True)
        )
        obsolete_ids = existing_ids.difference(incoming_ids)
        if obsolete_ids:
            logger.info(
                "%s: Removing %s obsolete contacts", character, len(obsolete_ids)
            )
            self.filter(character=character, eve_entity_id__in=obsolete_ids).delete()

        create_ids = incoming_ids.difference(existing_ids)
        if create_ids:
            self._create_new_contacts(
                character=character, contacts_list=contacts_list, contact_ids=create_ids
            )

        update_ids = incoming_ids.difference(create_ids)
        if update_ids:
            self._update_existing_contacts(
                character=character, contacts_list=contacts_list, contact_ids=update_ids
            )

        if not obsolete_ids and not create_ids and not update_ids:
            logger.info("%s: Contacts have not changed", character)

    def _create_new_contacts(
        self, character: models.Model, contacts_list: dict, contact_ids: list
    ):
        logger.info("%s: Storing %s new contacts", character, len(contact_ids))
        new_contacts_list = {
            contact_id: obj
            for contact_id, obj in contacts_list.items()
            if contact_id in contact_ids
        }
        new_contacts = [
            self.model(
                character=character,
                eve_entity=get_or_create_or_none("contact_id", contact_data, EveEntity),
                is_blocked=contact_data.get("is_blocked"),
                is_watched=contact_data.get("is_watched"),
                standing=contact_data.get("standing"),
            )
            for contact_data in new_contacts_list.values()
        ]
        self.bulk_create(new_contacts, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)
        self._update_contact_contact_labels(
            character=character,
            contacts_list=contacts_list,
            contact_ids=contact_ids,
            is_new=True,
        )

    def _update_contact_contact_labels(
        self,
        character: models.Model,
        contacts_list: dict,
        contact_ids: list,
        is_new=False,
    ):
        from ..models import CharacterContactLabel

        for contact_id, contact_data in contacts_list.items():
            if contact_id in contact_ids and contact_data.get("label_ids"):
                character_contact = self.filter(character=character).get(
                    eve_entity_id=contact_id
                )
                if not is_new:
                    character_contact.labels.clear()

                labels = list()
                for label_id in contact_data.get("label_ids"):
                    try:
                        label = character.contact_labels.get(label_id=label_id)
                    except CharacterContactLabel.DoesNotExist:
                        # sometimes label IDs on contacts
                        # do not refer to actual labels
                        logger.info(
                            "%s: Unknown contact label with id %s",
                            character,
                            label_id,
                        )
                    else:
                        labels.append(label)

                    character_contact.labels.add(*labels)

    def _update_existing_contacts(
        self, character: models.Model, contacts_list: dict, contact_ids: list
    ):
        logger.info("%s: Updating %s contacts", character, len(contact_ids))
        update_contact_pks = list(
            self.filter(character=character, eve_entity_id__in=contact_ids).values_list(
                "pk", flat=True
            )
        )
        contacts = self.in_bulk(update_contact_pks)
        for contact in contacts.values():
            contact_data = contacts_list.get(contact.eve_entity_id)
            if contact_data:
                contact.is_blocked = contact_data.get("is_blocked")
                contact.is_watched = contact_data.get("is_watched")
                contact.standing = contact_data.get("standing")

        self.bulk_update(
            contacts.values(),
            fields=["is_blocked", "is_watched", "standing"],
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )
        self._update_contact_contact_labels(
            character=character, contacts_list=contacts_list, contact_ids=contact_ids
        )


class CharacterContractManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, contracts_list):
        incoming_ids = set(contracts_list.keys())
        existing_ids = set(
            self.filter(character=character).values_list("contract_id", flat=True)
        )
        create_ids = incoming_ids.difference(existing_ids)
        if create_ids:
            self._create_new_contracts(
                character=character,
                contracts_list=contracts_list,
                contract_ids=create_ids,
            )
        update_ids = incoming_ids.difference(create_ids)
        if update_ids:
            self._update_existing_contracts(
                character=character,
                contracts_list=contracts_list,
                contract_ids=update_ids,
            )

    def _create_new_contracts(
        self, character: models.Model, contracts_list: dict, contract_ids: set
    ) -> None:
        from ..models import Location

        logger.info("%s: Storing %s new contracts", character, len(contract_ids))
        new_contracts = list()
        for contract_id in contract_ids:
            contract_data = contracts_list.get(contract_id)
            if contract_data:
                new_contracts.append(
                    self.model(
                        character=character,
                        contract_id=contract_data.get("contract_id"),
                        acceptor=get_or_create_or_none(
                            "acceptor_id", contract_data, EveEntity
                        ),
                        assignee=get_or_create_or_none(
                            "assignee_id", contract_data, EveEntity
                        ),
                        availability=self.model.ESI_AVAILABILITY_MAP[
                            contract_data.get("availability")
                        ],
                        buyout=contract_data.get("buyout"),
                        collateral=contract_data.get("collateral"),
                        contract_type=self.model.ESI_TYPE_MAP.get(
                            contract_data.get("type"),
                            self.model.TYPE_UNKNOWN,
                        ),
                        date_accepted=contract_data.get("date_accepted"),
                        date_completed=contract_data.get("date_completed"),
                        date_expired=contract_data.get("date_expired"),
                        date_issued=contract_data.get("date_issued"),
                        days_to_complete=contract_data.get("days_to_complete"),
                        end_location=get_or_none(
                            "end_location_id", contract_data, Location
                        ),
                        for_corporation=contract_data.get("for_corporation"),
                        issuer_corporation=get_or_create_or_none(
                            "issuer_corporation_id", contract_data, EveEntity
                        ),
                        issuer=get_or_create_or_none(
                            "issuer_id", contract_data, EveEntity
                        ),
                        price=contract_data.get("price"),
                        reward=contract_data.get("reward"),
                        start_location=get_or_none(
                            "start_location_id", contract_data, Location
                        ),
                        status=self.model.ESI_STATUS_MAP[contract_data.get("status")],
                        title=contract_data.get("title", ""),
                        volume=contract_data.get("volume"),
                    )
                )

        self.bulk_create(new_contracts, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

    def _update_existing_contracts(
        self, character: models.Model, contracts_list: dict, contract_ids: set
    ) -> None:
        logger.info("%s: Updating %s contracts", character, len(contract_ids))
        update_contract_pks = list(
            self.filter(character=character, contract_id__in=contract_ids).values_list(
                "pk", flat=True
            )
        )
        contracts = self.in_bulk(update_contract_pks)
        for contract in contracts.values():
            contract_data = contracts_list.get(contract.contract_id)
            if contract_data:
                contract.acceptor = get_or_create_or_none(
                    "acceptor_id", contract_data, EveEntity
                )
                contract.acceptor_corporation = get_or_create_or_none(
                    "acceptor_corporation_id", contract_data, EveEntity
                )
                contract.date_accepted = contract_data.get("date_accepted")
                contract.date_completed = contract_data.get("date_completed")
                contract.status = self.model.ESI_STATUS_MAP[contract_data.get("status")]

        self.bulk_update(
            contracts.values(),
            fields=[
                "acceptor",
                "acceptor_corporation",
                "date_accepted",
                "date_completed",
                "status",
            ],
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )


class CharacterContractBidManager(models.Manager):
    @transaction.atomic()
    def update_for_contract(self, contract: models.Model, bids_list):
        incoming_ids = set(bids_list.keys())
        existing_ids = set(
            self.filter(contract=contract).values_list("bid_id", flat=True)
        )
        create_ids = incoming_ids.difference(existing_ids)
        if not create_ids:
            logger.info(
                "%s, %s: No new contract bids to add",
                contract.character,
                contract.contract_id,
            )
            return

        logger.info(
            "%s, %s: Storing %s new contract bids",
            contract.character,
            contract.contract_id,
            len(create_ids),
        )
        bids = [
            self.model(
                contract=contract,
                bid_id=bid.get("bid_id"),
                amount=bid.get("amount"),
                bidder=get_or_create_or_none("bidder_id", bid, EveEntity),
                date_bid=bid.get("date_bid"),
            )
            for bid_id, bid in bids_list.items()
            if bid_id in create_ids
        ]
        self.bulk_create(bids, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)


class CharacterContractItemManager(models.Manager):
    def update_for_contract(self, contract: models.Model, items_data):
        logger.info(
            "%s, %s: Storing %s contract items",
            self,
            contract.contract_id,
            len(items_data),
        )
        items = [
            self.model(
                contract=contract,
                record_id=item.get("record_id"),
                is_included=item.get("is_included"),
                is_singleton=item.get("is_singleton"),
                quantity=item.get("quantity"),
                raw_quantity=item.get("raw_quantity"),
                eve_type=get_or_create_esi_or_none("type_id", item, EveType),
            )
            for item in items_data
            if "record_id" in item
        ]
        with transaction.atomic():
            self.filter(contract=contract).delete()
            self.bulk_create(items, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

    def annotate_pricing(self) -> models.QuerySet:
        """Returns qs with annotated price and total columns"""
        return (
            self.select_related("eve_type__market_price")
            .annotate(
                price=Case(
                    When(
                        raw_quantity=-2,
                        then=Value(None),
                    ),
                    default=F("eve_type__market_price__average_price"),
                )
            )
            .annotate(
                total=Case(
                    When(
                        raw_quantity=-2,
                        then=Value(None),
                    ),
                    default=ExpressionWrapper(
                        F("eve_type__market_price__average_price") * F("quantity"),
                        output_field=models.FloatField(),
                    ),
                )
            )
        )


class CharacterCorporationHistoryManager(models.Manager):
    def update_for_character(self, character: models.Model, history):
        entries = [
            self.model(
                character=character,
                record_id=row.get("record_id"),
                corporation=get_or_create_or_none("corporation_id", row, EveEntity),
                is_deleted=row.get("is_deleted"),
                start_date=row.get("start_date"),
            )
            for row in history
        ]
        with transaction.atomic():
            self.filter(character=character).delete()
            if entries:
                logger.info(
                    "%s: Creating %s entries for corporation history",
                    character,
                    len(entries),
                )
                self.bulk_create(entries)
            else:
                logger.info("%s: Corporation history is empty", character)

        if entries:
            EveEntity.objects.bulk_update_new_esi()


class CharacterDetailsManager(models.Manager):
    def update_for_character(self, character: models.Model, details):
        description = (
            details.get("description", "") if details.get("description") else ""
        )
        if description:
            eve_xml_to_html(description)  # resolve names early

        gender = (
            self.model.GENDER_MALE
            if details.get("gender") == "male"
            else self.model.GENDER_FEMALE
        )

        # Workaround because of ESI issue #1264
        # TODO: Remove once issue is fixed
        eve_ancestry = get_or_none("ancestry_id", details, EveAncestry)
        self.update_or_create(
            character=character,
            defaults={
                "alliance": get_or_create_or_none("alliance_id", details, EveEntity),
                "birthday": details.get("birthday"),
                "eve_ancestry": eve_ancestry,
                "eve_bloodline": get_or_create_esi_or_none(
                    "bloodline_id", details, EveBloodline
                ),
                "eve_faction": get_or_create_esi_or_none(
                    "faction_id", details, EveFaction
                ),
                "eve_race": get_or_create_esi_or_none("race_id", details, EveRace),
                "corporation": get_or_create_or_none(
                    "corporation_id", details, EveEntity
                ),
                "description": description,
                "gender": gender,
                "name": details.get("name", ""),
                "security_status": details.get("security_status"),
                "title": details.get("title", "") if details.get("title") else "",
            },
        )
        EveEntity.objects.bulk_update_new_esi()


class CharacterImplantManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, implants_data):
        self.filter(character=character).delete()
        if implants_data:
            implants = [
                self.model(
                    character=character,
                    eve_type=EveType.objects.get(id=eve_type_id),
                )
                for eve_type_id in implants_data
            ]
            logger.info("%s: Storing %s implants", character, len(implants))
            self.bulk_create(implants, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)
        else:
            logger.info("%s: No implants", character)


class CharacterLocationManager(models.Manager):
    def update_for_character(
        self, character: models.Model, token: Token, location_info
    ):
        from ..models.general import Location

        eve_solar_system, _ = EveSolarSystem.objects.get_or_create_esi(
            id=location_info.get("solar_system_id")
        )
        if location_info.get("station_id"):
            location, _ = Location.objects.get_or_create_esi_async(
                id=location_info.get("station_id"), token=token
            )
        elif location_info.get("structure_id"):
            location, _ = Location.objects.get_or_create_esi_async(
                id=location_info.get("structure_id"), token=token
            )
        else:
            location = None

        if eve_solar_system:
            self.update_or_create(
                character=character,
                defaults={
                    "eve_solar_system": eve_solar_system,
                    "location": location,
                },
            )


class CharacterLoyaltyEntryManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, loyalty_entries):
        self.filter(character=character).delete()
        new_entries = [
            self.model(
                character=character,
                corporation=get_or_create_or_none("corporation_id", entry, EveEntity),
                loyalty_points=entry.get("loyalty_points"),
            )
            for entry in loyalty_entries
            if "corporation_id" in entry and "loyalty_points" in entry
        ]
        self.bulk_create(new_entries, MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)


class CharacterJumpCloneManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character: models.Model, jump_clones_list: dict):
        from ..models import CharacterJumpCloneImplant, Location

        self.filter(character=character).delete()
        if not jump_clones_list:
            logger.info("%s: No jump clones", character)
            return

        logger.info("%s: Storing %s jump clones", character, len(jump_clones_list))
        jump_clones = [
            self.model(
                character=character,
                jump_clone_id=record.get("jump_clone_id"),
                location=get_or_none("location_id", record, Location),
                name=record.get("name") if record.get("name") else "",
            )
            for record in jump_clones_list
        ]
        self.bulk_create(
            jump_clones,
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )
        implants = list()
        for jump_clone_info in jump_clones_list:
            if jump_clone_info.get("implants"):
                for implant in jump_clone_info["implants"]:
                    jump_clone = character.jump_clones.get(
                        jump_clone_id=jump_clone_info.get("jump_clone_id")
                    )
                    implants.append(
                        CharacterJumpCloneImplant(
                            jump_clone=jump_clone,
                            eve_type=EveType.objects.get(id=implant),
                        )
                    )

        CharacterJumpCloneImplant.objects.bulk_create(
            implants,
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )


class CharacterMailManager(models.Manager):
    def update_for_character(
        self, character, cutoff_datetime, mail_headers, force_update
    ):
        if cutoff_datetime:
            self.filter(character=character, timestamp__lt=cutoff_datetime).delete()

        if force_update or character.has_section_changed(
            section=character.UpdateSection.MAILS, content=mail_headers
        ):
            self._preload_mail_senders(character=character, mail_headers=mail_headers)
            with transaction.atomic():
                incoming_ids = set(mail_headers.keys())
                existing_ids = set(
                    self.filter(character=character).values_list("mail_id", flat=True)
                )
                create_ids = incoming_ids.difference(existing_ids)
                if create_ids:
                    self._create_mail_headers(
                        character=character,
                        mail_headers=mail_headers,
                        create_ids=create_ids,
                    )

                update_ids = incoming_ids.difference(create_ids)
                if update_ids:
                    self._update_mail_headers(
                        character=character,
                        mail_headers=mail_headers,
                        update_ids=update_ids,
                    )

                if not create_ids and not update_ids:
                    logger.info("%s: No mails", character)

            character.update_section_content_hash(
                section=character.UpdateSection.MAILS, content=mail_headers
            )

        else:
            logger.info("%s: Mails have not changed", character)

    def _preload_mail_senders(self, character, mail_headers):
        from ..models import MailEntity

        incoming_ids = set(mail_headers.keys())
        existing_ids = set(
            self.filter(character=character).values_list("mail_id", flat=True)
        )
        create_ids = incoming_ids.difference(existing_ids)
        if create_ids:
            new_mail_headers_list = character._headers_list_subset(
                mail_headers, create_ids
            )
            for mail_id, header in new_mail_headers_list.items():
                MailEntity.objects.get_or_create_esi_async(header.get("from"))

    def _create_mail_headers(self, character, mail_headers: dict, create_ids) -> None:
        from ..models import MailEntity

        logger.info("%s: Create %s new mail headers", character, len(create_ids))
        new_mail_headers_list = character._headers_list_subset(mail_headers, create_ids)
        self._add_missing_mailing_lists_from_recipients(
            character=character, new_mail_headers_list=new_mail_headers_list
        )

        # create headers
        new_headers = list()
        for mail_id, header in new_mail_headers_list.items():
            new_headers.append(
                self.model(
                    character=character,
                    mail_id=mail_id,
                    sender=get_or_none("from", header, MailEntity),
                    is_read=bool(header.get("is_read")),
                    subject=header.get("subject", ""),
                    timestamp=header.get("timestamp"),
                )
            )

        self.bulk_create(new_headers, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

        # add recipients and labels
        labels = character.mail_labels.get_all_labels()
        for mail_id, header in new_mail_headers_list.items():
            mail_obj = self.filter(character=character).get(mail_id=mail_id)
            recipients = list()
            recipient_type_map = {
                "alliance": MailEntity.Category.ALLIANCE,
                "character": MailEntity.Category.CHARACTER,
                "corporation": MailEntity.Category.CORPORATION,
                "mailing_list": MailEntity.Category.MAILING_LIST,
            }
            for recipient_info in header.get("recipients"):
                recipient, _ = MailEntity.objects.get_or_create(
                    id=recipient_info.get("recipient_id"),
                    defaults={
                        "category": recipient_type_map[
                            recipient_info.get("recipient_type")
                        ]
                    },
                )
                recipients.append(recipient)

            mail_obj.recipients.set(recipients, clear=True)
            MailEntity.objects.bulk_update_names(recipients, keep_names=True)
            self._update_labels_of_mail(
                character=character,
                mail=mail_obj,
                label_ids=header.get("labels"),
                labels=labels,
            )

    def _add_missing_mailing_lists_from_recipients(
        self, character, new_mail_headers_list
    ):
        """Add mailing lists from recipients that are not part of the known
        mailing lists"""
        from ..models import MailEntity

        incoming_ids = set()
        for header in new_mail_headers_list.values():
            for recipient in header.get("recipients"):
                if recipient.get("recipient_type") == "mailing_list":
                    incoming_ids.add(recipient.get("recipient_id"))

        existing_ids = set(
            MailEntity.objects.filter(
                category=MailEntity.Category.MAILING_LIST
            ).values_list("id", flat=True)
        )
        create_ids = incoming_ids.difference(existing_ids)
        if create_ids:
            logger.info(
                "%s: Adding %s unknown mailing lists from recipients",
                character,
                len(create_ids),
            )
            for list_id in create_ids:
                MailEntity.objects.get_or_create(
                    id=list_id, defaults={"category": MailEntity.Category.MAILING_LIST}
                )

    def _update_labels_of_mail(
        self, character, mail: models.Model, label_ids: List[int], labels: list
    ) -> None:
        """Updates the labels of a mail object from a dict"""
        mail.labels.clear()
        if label_ids:
            labels_to_add = list()
            for label_id in label_ids:
                try:
                    labels_to_add.append(labels[label_id])
                except KeyError:
                    logger.info(
                        "%s: Unknown mail label with ID %s for mail %s",
                        character,
                        label_id,
                        mail,
                    )

            mail.labels.add(*labels_to_add)

    def _update_mail_headers(self, character, mail_headers: dict, update_ids) -> None:
        logger.info("%s: Updating %s mail headers", character, len(update_ids))
        mail_pks = self.filter(character=character, mail_id__in=update_ids).values_list(
            "pk", flat=True
        )
        labels = character.mail_labels.get_all_labels()
        mails = self.in_bulk(mail_pks)
        for mail in mails.values():
            mail_header = mail_headers.get(mail.mail_id)
            if mail_header:
                mail.is_read = bool(mail_header.get("is_read"))
                self._update_labels_of_mail(
                    character=character,
                    mail=mail,
                    label_ids=mail_header.get("labels"),
                    labels=labels,
                )

        self.bulk_update(mails.values(), ["is_read"])


class CharacterMailLabelManager(models.Manager):
    def get_all_labels(self) -> Dict[int, models.Model]:
        """Returns all label objects as dict by label_id"""
        label_pks = self.values_list("pk", flat=True)
        return {label.label_id: label for label in self.in_bulk(label_pks).values()}

    @transaction.atomic()
    def update_for_character(self, character: models.Model, mail_labels_list: dict):
        logger.info("%s: Storing %s mail labels", character, len(mail_labels_list))
        incoming_ids = set(mail_labels_list.keys())
        existing_ids = set(
            self.filter(character=character).values_list("label_id", flat=True)
        )
        obsolete_ids = existing_ids.difference(incoming_ids)
        if obsolete_ids:
            self.filter(character=character, label_id__in=obsolete_ids).delete()

        create_ids = incoming_ids.difference(existing_ids)
        if create_ids:
            self._create_new_mail_labels(
                character=character,
                mail_labels_list=mail_labels_list,
                label_ids=create_ids,
            )

        update_ids = incoming_ids.difference(create_ids)
        if update_ids:
            self._update_existing_mail_labels(
                character=character,
                mail_labels_list=mail_labels_list,
                label_ids=update_ids,
            )

    def _create_new_mail_labels(
        self, character, mail_labels_list: dict, label_ids: set
    ):
        new_labels = [
            self.model(
                character=character,
                label_id=label.get("label_id"),
                color=label.get("color"),
                name=label.get("name"),
                unread_count=label.get("unread_count"),
            )
            for label_id, label in mail_labels_list.items()
            if label_id in label_ids
        ]
        self.bulk_create(new_labels, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

    def _update_existing_mail_labels(
        self, character, mail_labels_list: dict, label_ids: set
    ):
        logger.info("%s: Updating %s mail labels", character, len(label_ids))
        update_pks = list(
            self.filter(character=character, label_id__in=label_ids).values_list(
                "pk", flat=True
            )
        )
        labels = self.in_bulk(update_pks)
        for label in labels.values():
            record = mail_labels_list.get(label.label_id)
            if record:
                label.name = record.get("name")
                label.color = record.get("color")
                label.unread_count = record.get("unread_count")

        self.bulk_update(
            labels.values(),
            fields=["name", "color", "unread_count"],
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )


class CharacterShipManager(models.Manager):
    def update_for_character(self, character: models.Model, ship_info: dict):
        eve_type, _ = EveType.objects.get_or_create_esi(
            id=ship_info.get("ship_type_id")
        )
        self.update_or_create(
            character=character,
            defaults={
                "eve_type": eve_type,
                "name": ship_info["ship_name"],
            },
        )


class CharacterSkillqueueEntryManager(models.Manager):
    def update_for_character(self, character: models.Model, skillqueue):
        # TODO: Replace delete + create with create + update
        if skillqueue:
            entries = [
                self.model(
                    character=character,
                    eve_type=get_or_create_esi_or_none("skill_id", entry, EveType),
                    finish_date=entry.get("finish_date"),
                    finished_level=entry.get("finished_level"),
                    level_end_sp=entry.get("level_end_sp"),
                    level_start_sp=entry.get("level_start_sp"),
                    queue_position=entry.get("queue_position"),
                    start_date=entry.get("start_date"),
                    training_start_sp=entry.get("training_start_sp"),
                )
                for entry in skillqueue
            ]
        else:
            entries = list()
        with transaction.atomic():
            self.filter(character=character).delete()
            if entries:
                logger.info(
                    "%s: Writing skill queue of size %s", character, len(entries)
                )
                self.bulk_create(
                    entries, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE
                )
            else:
                logger.info("%s: Skill queue is empty", character)


class CharacterSkillManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character, skills_list):
        incoming_ids = set(skills_list.keys())
        existing_ids = set(
            self.filter(character=character).values_list("eve_type_id", flat=True)
        )
        obsolete_ids = existing_ids.difference(incoming_ids)
        if obsolete_ids:
            logger.info("%s: Removing %s obsolete skills", character, len(obsolete_ids))
            self.filter(character=character, eve_type_id__in=obsolete_ids).delete()

        create_ids = None
        update_ids = None
        if skills_list:
            create_ids = incoming_ids.difference(existing_ids)
            if create_ids:
                self._create_from_dict(
                    character=character, skills_list=skills_list, create_ids=create_ids
                )

            update_ids = incoming_ids.difference(create_ids)
            if update_ids:
                self._update_from_dict(
                    character=character, skills_list=skills_list, update_ids=update_ids
                )

        if not obsolete_ids and not create_ids and not update_ids:
            logger.info("%s: Skills have not changed", character)

    def _create_from_dict(self, character, skills_list: dict, create_ids: list):
        logger.info("%s: Storing %s new skills", character, len(create_ids))
        skills = [
            self.model(
                character=character,
                eve_type=EveType.objects.get(id=skill_info.get("skill_id")),
                active_skill_level=skill_info.get("active_skill_level"),
                skillpoints_in_skill=skill_info.get("skillpoints_in_skill"),
                trained_skill_level=skill_info.get("trained_skill_level"),
            )
            for skill_id, skill_info in skills_list.items()
            if skill_id in create_ids
        ]
        self.bulk_create(skills, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

    def _update_from_dict(self, character, skills_list: dict, update_ids: list):
        logger.info("%s: Updating %s skills", character, len(update_ids))
        update_pks = list(
            self.filter(character=character, eve_type_id__in=update_ids).values_list(
                "pk", flat=True
            )
        )
        skills = self.in_bulk(update_pks)
        for skill in skills.values():
            skill_info = skills_list.get(skill.eve_type_id)
            if skill_info:
                skill.active_skill_level = skill_info.get("active_skill_level")
                skill.skillpoints_in_skill = skill_info.get("skillpoints_in_skill")
                skill.trained_skill_level = skill_info.get("trained_skill_level")

        self.bulk_update(
            skills.values(),
            fields=[
                "active_skill_level",
                "skillpoints_in_skill",
                "trained_skill_level",
            ],
            batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE,
        )


class CharacterSkillSetCheckManager(models.Manager):
    @transaction.atomic()
    def update_for_character(self, character):
        from ..models import SkillSet

        character_skills = {
            obj["eve_type_id"]: obj["active_skill_level"]
            for obj in character.skills.values("eve_type_id", "active_skill_level")
        }
        self.filter(character=character).all().delete()
        skill_sets_qs = SkillSet.objects.prefetch_related(
            "skills", "skills__eve_type"
        ).all()
        skill_sets_count = skill_sets_qs.count()
        if skill_sets_count == 0:
            logger.info("%s: No skill sets defined", character)
            return

        logger.info("%s: Checking %s skill sets", character, skill_sets_count)
        skill_set_checks = [
            self.model(character=character, skill_set=skill_set)
            for skill_set in skill_sets_qs
        ]
        self.bulk_create(
            skill_set_checks, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE
        )

        # add failed recommended / required skills to objects if any
        obj_pks = list(self.filter(character=character).values_list("pk", flat=True))
        skill_set_checks = self.in_bulk(obj_pks)
        checks_by_skill_set_id = {
            obj.skill_set_id: obj for obj in skill_set_checks.values()
        }

        # required skills
        for skill_set in skill_sets_qs:
            failed_skills = self._identify_failed_skills(
                skill_set, character_skills, "required"
            )
            if failed_skills:
                checks_by_skill_set_id[skill_set.id].failed_required_skills.add(
                    *failed_skills
                )

        # required skills
        for skill_set in skill_sets_qs:
            failed_skills = self._identify_failed_skills(
                skill_set, character_skills, "recommended"
            )
            if failed_skills:
                checks_by_skill_set_id[skill_set.id].failed_recommended_skills.add(
                    *failed_skills
                )

    @staticmethod
    def _identify_failed_skills(
        skill_set: models.Model, character_skills: dict, level_name: str
    ) -> list:
        failed_skills = list()
        kwargs = {f"{level_name}_level__isnull": False}
        for skill in skill_set.skills.filter(**kwargs):
            eve_type_id = skill.eve_type_id
            if eve_type_id not in character_skills or character_skills[
                eve_type_id
            ] < getattr(skill, f"{level_name}_level"):
                failed_skills.append(skill)

        return failed_skills


class CharacterWalletJournalEntryManager(models.Manager):
    def update_for_character(
        self, character: models.Model, cutoff_datetime: dt.datetime, journal: list
    ):
        entries_list = {
            obj.get("id"): obj
            for obj in journal
            if cutoff_datetime is None or obj.get("date") > cutoff_datetime
        }
        if cutoff_datetime:
            self.filter(character=character, date__lt=cutoff_datetime).delete()

        with transaction.atomic():
            incoming_ids = set(entries_list.keys())
            existing_ids = set(self.values_list("entry_id", flat=True))
            create_ids = incoming_ids.difference(existing_ids)
            if not create_ids:
                logger.info("%s: No new wallet journal entries", character)
                return

            logger.info(
                "%s: Adding %s new wallet journal entries", character, len(create_ids)
            )
            entries = [
                self.model(
                    character=character,
                    entry_id=entry_id,
                    amount=row.get("amount"),
                    balance=row.get("balance"),
                    context_id=row.get("context_id"),
                    context_id_type=(
                        self.model.match_context_type_id(row.get("context_id_type"))
                    ),
                    date=row.get("date"),
                    description=row.get("description"),
                    first_party=get_or_create_or_none("first_party_id", row, EveEntity),
                    reason=row.get("reason", ""),
                    ref_type=row.get("ref_type"),
                    second_party=get_or_create_or_none(
                        "second_party_id", row, EveEntity
                    ),
                    tax=row.get("tax"),
                    tax_receiver=row.get("tax_receiver"),
                )
                for entry_id, row in entries_list.items()
                if entry_id in create_ids
            ]
            self.bulk_create(entries, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)


class CharacterWalletTransactionManager(models.Manager):
    def update_for_character(self, character, cutoff_datetime, transactions, token):
        from ..models import Location

        transaction_list = {
            obj.get("transaction_id"): obj
            for obj in transactions
            if cutoff_datetime is None or obj.get("date") > cutoff_datetime
        }
        if cutoff_datetime:
            self.filter(character=character, date__lt=cutoff_datetime).delete()

        incoming_location_ids = {
            row.get("location_id") for row in transaction_list.values()
        }
        character._preload_all_locations(token, incoming_location_ids)
        type_ids = {row.get("type_id") for row in transaction_list.values()}
        EveType.objects.bulk_get_or_create_esi(ids=type_ids)

        with transaction.atomic():
            incoming_ids = set(transaction_list.keys())
            existing_ids = set(self.values_list("transaction_id", flat=True))
            create_ids = incoming_ids.difference(existing_ids)
            if not create_ids:
                logger.info("%s: No new wallet transcations", character)
                return

            logger.info(
                "%s: Adding %s new wallet transactions",
                character,
                len(create_ids),
            )
            entries = []
            for transaction_id, row in transaction_list.items():
                if transaction_id in create_ids:
                    try:
                        journal_entry = character.wallet_journal.get(
                            entry_id=row.get("journal_ref_id")
                        )
                    except character.wallet_journal.model.DoesNotExist:
                        journal_entry = None
                    entries.append(
                        self.model(
                            character=character,
                            transaction_id=transaction_id,
                            client=get_or_create_or_none("client_id", row, EveEntity),
                            date=row.get("date"),
                            is_buy=row.get("is_buy"),
                            is_personal=row.get("is_personal"),
                            journal_ref=journal_entry,
                            location=get_or_none("location_id", row, Location),
                            eve_type=EveType.objects.get(id=row.get("type_id")),
                            quantity=row.get("quantity"),
                            unit_price=row.get("unit_price"),
                        )
                    )
            self.bulk_create(entries, batch_size=MEMBERAUDIT_BULK_METHODS_BATCH_SIZE)

        EveEntity.objects.bulk_update_new_esi()


class CharacterAttributesManager(models.Manager):
    def update_for_character(self, character, attribute_data):
        self.update_or_create(
            character=character,
            defaults={
                "accrued_remap_cooldown_date": attribute_data.get(
                    "accrued_remap_cooldown_date"
                ),
                "last_remap_date": attribute_data.get("last_remap_date"),
                "bonus_remaps": attribute_data.get("bonus_remaps"),
                "charisma": attribute_data.get("charisma"),
                "intelligence": attribute_data.get("intelligence"),
                "memory": attribute_data.get("memory"),
                "perception": attribute_data.get("perception"),
                "willpower": attribute_data.get("willpower"),
            },
        )
