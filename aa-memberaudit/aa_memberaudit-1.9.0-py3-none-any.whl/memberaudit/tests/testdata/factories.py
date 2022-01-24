"""Factories for creating test objects with defaults."""
import datetime as dt

from django.db import models
from django.utils.timezone import now

from ...models import (
    CharacterContract,
    CharacterContractItem,
    CharacterWalletJournalEntry,
)


def create_wallet_journal_entry(**kwargs) -> models.Model:
    params = {
        "entry_id": 1,
        "amount": 1000000.0,
        "balance": 20000000.0,
        "ref_type": "player_donation",
        "context_id_type": CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
        "date": now(),
        "description": "test description",
        "first_party_id": 1001,
        "second_party_id": 1002,
        "reason": "test reason",
    }
    params.update(kwargs)
    return CharacterWalletJournalEntry.objects.create(**params)


def create_contract(**kwargs) -> models.Model:
    date_issed = now() if "date_issued" not in kwargs else kwargs["date_issued"]
    params = {
        "contract_id": 1,
        "availability": CharacterContract.AVAILABILITY_PERSONAL,
        "contract_type": CharacterContract.TYPE_ITEM_EXCHANGE,
        "assignee_id": 1002,
        "date_issued": date_issed,
        "date_expired": date_issed + dt.timedelta(days=3),
        "for_corporation": False,
        "issuer_id": 1001,
        "issuer_corporation_id": 2001,
        "status": CharacterContract.STATUS_OUTSTANDING,
        "title": "Dummy info",
    }
    params.update(kwargs)
    return CharacterContract.objects.create(**params)


def create_contract_item(**kwargs) -> models.Model:
    params = {
        "record_id": 1,
        "is_included": True,
        "is_singleton": False,
        "quantity": 1,
        "eve_type_id": 603,
    }
    params.update(kwargs)
    return CharacterContractItem.objects.create(**params)
