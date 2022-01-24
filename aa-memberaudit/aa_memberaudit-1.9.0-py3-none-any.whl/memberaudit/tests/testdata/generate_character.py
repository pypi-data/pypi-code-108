# flake8: noqa
"""
This is a standalone scripts that generates a test character
"""

import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
myauth_dir = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(currentdir))))
    + "/myauth"
)
sys.path.insert(0, myauth_dir)


import django
from django.apps import apps

# init and setup django project
print("Initializing Django...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
django.setup()

if not apps.is_installed("memberaudit"):
    raise RuntimeError("The app memberaudit is not installed")

import datetime as dt
import random

from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from eveuniverse.models import EveEntity, EveSolarSystem

from allianceauth.eveonline.models import EveCharacter

from memberaudit.models import (
    CharacterDetails,
    CharacterLocation,
    CharacterWalletJournalEntry,
)
from memberaudit.tests import create_memberaudit_character

WALLET_JOURNAL_ENTRIES = 100_000


def main():
    eve_character, corporation, character = recreate_character()
    create_details(eve_character, corporation, character)
    create_location(character)
    create_wallet_journal(eve_character, character)
    print("DONE")


def recreate_character():
    print("Recreating character...")
    eve_character, _ = EveCharacter.objects.get_or_create(
        character_id=92532650,
        defaults={
            "character_name": "CCP Falcon",
            "corporation_id": 1000127,
            "corporation_name": "Guristas",
            "corporation_ticker": "XXX",
        },
    )
    corporation, _ = EveEntity.objects.get_or_create_esi(
        id=eve_character.corporation_id
    )
    try:
        eve_character.character_ownership.user.delete()
    except ObjectDoesNotExist:
        pass
    character = create_memberaudit_character(92532650)
    return eve_character, corporation, character


def create_details(eve_character, corporation, character):
    CharacterDetails.objects.create(
        character=character,
        birthday=now(),
        corporation=corporation,
        description="This is a generated test character.",
        eve_bloodline_id=1,
        eve_race_id=1,
        name=eve_character.character_name,
    )


def create_location(character):
    eve_solar_system, _ = EveSolarSystem.objects.get_or_create_esi(id=30004984)
    CharacterLocation.objects.create(
        character=character, eve_solar_system=eve_solar_system
    )


def create_wallet_journal(eve_character, character):
    print(f"Creating wallet journal with {WALLET_JOURNAL_ENTRIES} entries...")
    first_party, _ = EveEntity.objects.get_or_create_esi(id=eve_character.character_id)
    some_characters = list(
        EveEntity.objects.filter(category=EveEntity.CATEGORY_CHARACTER).order_by("?")[
            :20
        ]
    )
    objs = list()
    balance = 10_000_000_000_000
    date = now() - dt.timedelta(days=5_000)
    for entry_id in range(1, WALLET_JOURNAL_ENTRIES):
        amount = random.randint(1_000_000, 100_000_000)
        balance -= amount
        second_party = random.choice(some_characters)
        date += dt.timedelta(minutes=random.randint(1, 15))
        objs.append(
            CharacterWalletJournalEntry(
                character=character,
                entry_id=entry_id,
                amount=amount,
                balance=balance,
                context_id_type=CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
                date=date,
                description=f"Generated entry #{entry_id}",
                first_party=first_party,
                second_party=second_party,
                ref_type="player_donation",
            )
        )
    CharacterWalletJournalEntry.objects.bulk_create(objs, batch_size=500)


main()
