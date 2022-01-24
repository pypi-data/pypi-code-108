import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command

from app_utils.testing import NoSocketsTestCase

from ..models import Character
from . import (
    add_auth_character_to_user,
    create_memberaudit_character,
    create_user_from_evecharacter_with_access,
)
from .testdata.factories import create_contract, create_contract_item
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse

PACKAGE_PATH = "memberaudit.management.commands"
DATA_EXPORTERS_PATH = "memberaudit.core.data_exporters"


class TestResetCharacters(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_entities()
        Character.objects.all().delete()

    def test_normal(self):
        """can recreate member audit characters from main and alt of matching tokens"""
        user, co_1001 = create_user_from_evecharacter_with_access(1001)
        co_1002 = add_auth_character_to_user(user, 1002)

        out = StringIO()
        call_command("memberaudit_reset_characters", "--noinput", stdout=out)

        self.assertSetEqual(
            set(Character.objects.values_list("character_ownership_id", flat=True)),
            {co_1001.id, co_1002.id},
        )

    def test_orphaned_tokens(self):
        """
        given a matching token exists and the respective auth character
        is now owner by another user
        and no longer has a matching token
        when creating member audit characters
        then no member audit character is created for the switched auth character
        """
        user_1, co_1001 = create_user_from_evecharacter_with_access(1001)
        add_auth_character_to_user(user_1, 1002)
        user_2, co_1101 = create_user_from_evecharacter_with_access(1101)

        # re-add auth character 1002 to another user, but without member audit scopes
        add_auth_character_to_user(user_2, 1002, scopes="publicData")

        out = StringIO()
        call_command("memberaudit_reset_characters", "--noinput", stdout=out)

        self.assertSetEqual(
            set(Character.objects.values_list("character_ownership_id", flat=True)),
            {co_1001.id, co_1101.id},
        )


class TestDataExport(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_entities()
        load_eveuniverse()
        cls.character = create_memberaudit_character(1001)

    def test_should_export_contract_item(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # given
            contract = create_contract(character=self.character)
            create_contract_item(contract=contract, record_id=12)
            out = StringIO()
            # when
            call_command(
                "memberaudit_data_export",
                "contract-item",
                "--destination",
                tmpdirname,
                stdout=out,
            )
            # then
            output_file = Path(tmpdirname) / Path(
                "memberaudit_contract-item"
            ).with_suffix(".csv")
            self.assertTrue(output_file.exists())
