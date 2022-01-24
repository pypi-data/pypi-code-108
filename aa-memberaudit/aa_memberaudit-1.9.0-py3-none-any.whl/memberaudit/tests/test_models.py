import datetime as dt
import hashlib
import json
from unittest.mock import Mock, patch

from bravado.exception import HTTPNotFound
from pytz import UTC

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now
from esi.errors import TokenError
from esi.models import Token
from eveuniverse.models import EveEntity, EveMarketPrice, EveSolarSystem, EveType

from allianceauth.tests.auth_utils import AuthUtils
from app_utils.esi import EsiStatus
from app_utils.esi_testing import BravadoResponseStub
from app_utils.testing import NoSocketsTestCase, queryset_pks

from ..core.xml_converter import eve_xml_to_html
from ..models import (
    Character,
    CharacterAttributes,
    CharacterContact,
    CharacterContactLabel,
    CharacterContract,
    CharacterContractBid,
    CharacterContractItem,
    CharacterDetails,
    CharacterMail,
    CharacterMailLabel,
    CharacterShip,
    CharacterSkill,
    CharacterSkillqueueEntry,
    CharacterUpdateStatus,
    CharacterWalletJournalEntry,
    General,
    Location,
    MailEntity,
    SkillSet,
    SkillSetGroup,
    SkillSetSkill,
)
from ..models.character import data_retention_cutoff
from . import (
    add_memberaudit_character_to_user,
    create_memberaudit_character,
    create_user_from_evecharacter_with_access,
    scope_names_set,
)
from .testdata.esi_client_stub import esi_client_stub
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse
from .testdata.load_locations import load_locations

MODELS_PATH = "memberaudit.models"
MANAGERS_PATH = "memberaudit.managers"
TASKS_PATH = "memberaudit.tasks"


class TestCharacterContract(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.character_1002 = create_memberaudit_character(1002)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()
        cls.jita = EveSolarSystem.objects.get(id=30000142)
        cls.jita_44 = Location.objects.get(id=60003760)
        cls.amamake = EveSolarSystem.objects.get(id=30002537)
        cls.structure_1 = Location.objects.get(id=1000000000001)
        cls.item_type_1 = EveType.objects.get(id=19540)
        cls.item_type_2 = EveType.objects.get(id=19551)

    def setUp(self) -> None:
        self.contract = CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=42,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_ITEM_EXCHANGE,
            date_issued=now(),
            date_expired=now() + dt.timedelta(days=3),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_OUTSTANDING,
            start_location=self.jita_44,
            end_location=self.jita_44,
        )
        self.contract_completed = CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=43,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_ITEM_EXCHANGE,
            date_issued=now() - dt.timedelta(days=3),
            date_completed=now() - dt.timedelta(days=2),
            date_expired=now() - dt.timedelta(days=1),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_FINISHED,
            start_location=self.jita_44,
            end_location=self.jita_44,
        )

    def test_str(self):
        self.assertEqual(str(self.contract), f"{self.character_1001}-42")

    def test_is_completed(self):
        self.assertFalse(self.contract.is_completed)
        self.assertTrue(self.contract_completed.is_completed)

    def test_has_expired(self):
        self.assertFalse(self.contract.has_expired)
        self.assertTrue(self.contract_completed.has_expired)

    def test_hours_issued_2_completed(self):
        self.assertIsNone(self.contract.hours_issued_2_completed)
        self.assertEqual(self.contract_completed.hours_issued_2_completed, 24)

    def test_summary_one_item_1(self):
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=1,
            is_included=True,
            is_singleton=False,
            quantity=1,
            eve_type=self.item_type_1,
        )
        self.assertEqual(self.contract.summary(), "High-grade Snake Alpha")

    def test_summary_one_item_2(self):
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=1,
            is_included=True,
            is_singleton=False,
            quantity=1,
            eve_type=self.item_type_1,
        )
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=2,
            is_included=False,
            is_singleton=False,
            quantity=1,
            eve_type=self.item_type_2,
        )
        self.assertEqual(self.contract.summary(), "High-grade Snake Alpha")

    def test_summary_multiple_item(self):
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=1,
            is_included=True,
            is_singleton=False,
            quantity=1,
            eve_type=self.item_type_1,
        ),
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=2,
            is_included=True,
            is_singleton=False,
            quantity=1,
            eve_type=self.item_type_2,
        )
        self.assertEqual(self.contract.summary(), "[Multiple Items]")

    def test_summary_no_items(self):
        self.assertEqual(self.contract.summary(), "(no items)")

    def test_can_calculate_pricing_1(self):
        """calculate price and total for normal item"""
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=1,
            is_included=True,
            is_singleton=False,
            quantity=2,
            eve_type=self.item_type_1,
        ),
        EveMarketPrice.objects.create(eve_type=self.item_type_1, average_price=5000000)
        qs = self.contract.items.annotate_pricing()
        item_1 = qs.get(record_id=1)
        self.assertEqual(item_1.price, 5000000)
        self.assertEqual(item_1.total, 10000000)

    def test_can_calculate_pricing_2(self):
        """calculate price and total for BPO"""
        CharacterContractItem.objects.create(
            contract=self.contract,
            record_id=1,
            is_included=True,
            is_singleton=False,
            quantity=1,
            raw_quantity=-2,
            eve_type=self.item_type_1,
        ),
        EveMarketPrice.objects.create(eve_type=self.item_type_1, average_price=5000000)
        qs = self.contract.items.annotate_pricing()
        item_1 = qs.get(record_id=1)
        self.assertIsNone(item_1.price)
        self.assertIsNone(item_1.total)


class TestCharacterFetchToken(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def setUp(self) -> None:
        self.character = create_memberaudit_character(1001)

    def test_defaults(self):
        token = self.character.fetch_token()
        self.assertIsInstance(token, Token)
        self.assertSetEqual(scope_names_set(token), set(Character.get_esi_scopes()))

    def test_specified_scope(self):
        token = self.character.fetch_token("esi-mail.read_mail.v1")
        self.assertIsInstance(token, Token)
        self.assertIn("esi-mail.read_mail.v1", scope_names_set(token))

    @patch(MODELS_PATH + ".character.notify_throttled")
    def test_should_raise_exception_and_notify_user_if_not_found(
        self, mock_notify_throttled
    ):
        # when
        with self.assertRaises(TokenError):
            self.character.fetch_token("invalid_scope")
        # then
        self.assertTrue(mock_notify_throttled.called)
        _, kwargs = mock_notify_throttled.call_args
        self.assertEqual(kwargs["user"], self.character.character_ownership.user)


class TestCharacterSkillQueue(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.skill_type_1 = EveType.objects.get(id=24311)
        cls.skill_type_2 = EveType.objects.get(id=24312)

    def test_is_active_1(self):
        """when training is active and skill is in first position then return True"""
        entry = CharacterSkillqueueEntry.objects.create(
            character=self.character_1001,
            eve_type=self.skill_type_1,
            finish_date=now() + dt.timedelta(days=3),
            finished_level=5,
            queue_position=0,
            start_date=now() - dt.timedelta(days=1),
        )
        self.assertTrue(entry.is_active)

    def test_is_active_2(self):
        """when training is active and skill is not in first position then return False"""
        entry = CharacterSkillqueueEntry.objects.create(
            character=self.character_1001,
            eve_type=self.skill_type_1,
            finish_date=now() + dt.timedelta(days=3),
            finished_level=5,
            queue_position=1,
            start_date=now() - dt.timedelta(days=1),
        )
        self.assertFalse(entry.is_active)

    def test_is_active_3(self):
        """when training is not active and skill is in first position then return False"""
        entry = CharacterSkillqueueEntry.objects.create(
            character=self.character_1001,
            eve_type=self.skill_type_1,
            finished_level=5,
            queue_position=0,
        )
        self.assertFalse(entry.is_active)


class TestCharacterUpdateBase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.character_1002 = create_memberaudit_character(1002)
        cls.corporation_2001 = EveEntity.objects.get(id=2001)
        cls.corporation_2002 = EveEntity.objects.get(id=2002)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()
        cls.jita = EveSolarSystem.objects.get(id=30000142)
        cls.jita_44 = Location.objects.get(id=60003760)
        cls.amamake = EveSolarSystem.objects.get(id=30002537)
        cls.structure_1 = Location.objects.get(id=1000000000001)


class TestCharacterUpdateSection(NoSocketsTestCase):
    def test_method_name(self):
        result = Character.UpdateSection.method_name(
            Character.UpdateSection.CORPORATION_HISTORY
        )
        self.assertEqual(result, "update_corporation_history")

        with self.assertRaises(ValueError):
            result = Character.UpdateSection.method_name("invalid")

    def test_display_name(self):
        result = Character.UpdateSection.display_name(
            Character.UpdateSection.CORPORATION_HISTORY
        )
        self.assertEqual(result, "corporation history")

        with self.assertRaises(ValueError):
            result = Character.UpdateSection.display_name("invalid")


class TestCharacterUpdateStatus(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.content = {"alpha": 1, "bravo": 2}

    def test_reset_1(self):
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            last_error_message="abc",
        )
        status.reset()
        status.refresh_from_db()

        self.assertIsNone(status.is_success)
        self.assertEqual(status.last_error_message, "")
        self.assertEqual(status.root_task_id, "")
        self.assertEqual(status.parent_task_id, "")

    def test_reset_2(self):
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            last_error_message="abc",
        )
        status.reset(root_task_id="1", parent_task_id="2")
        status.refresh_from_db()

        self.assertIsNone(status.is_success)
        self.assertEqual(status.last_error_message, "")
        self.assertEqual(status.root_task_id, "1")
        self.assertEqual(status.parent_task_id, "2")

    def test_has_changed_1(self):
        """When hash is different, then return True"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            content_hash_1="abc",
        )
        self.assertTrue(status.has_changed(self.content))

    def test_has_changed_2(self):
        """When no hash exists, then return True"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            content_hash_1="",
        )
        self.assertTrue(status.has_changed(self.content))

    def test_has_changed_3a(self):
        """When hash is equal, then return False"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            content_hash_1=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertFalse(status.has_changed(self.content))

    def test_has_changed_3b(self):
        """When hash is equal, then return False"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            content_hash_2=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertFalse(status.has_changed(content=self.content, hash_num=2))

    def test_has_changed_3c(self):
        """When hash is equal, then return False"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            content_hash_3=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertFalse(status.has_changed(content=self.content, hash_num=3))

    def test_is_updating_1(self):
        """When started_at exist and finished_at does not exist, return True"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            started_at=now(),
        )
        self.assertTrue(status.is_updating)

    def test_is_updating_2(self):
        """When started_at and finished_at does not exist, return False"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            started_at=now(),
            finished_at=now(),
        )
        self.assertFalse(status.is_updating)

    def test_is_updating_3(self):
        """When started_at and finished_at both do not exist, return False"""
        status = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
        )
        self.assertFalse(status.is_updating)


class TestCharacterUpdateSectionMethods(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.section = Character.UpdateSection.ASSETS
        cls.content = {"alpha": 1, "bravo": 2}

    def test_reset_1(self):
        """when section exists, reset it"""
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=self.section,
            is_success=False,
            last_error_message="abc",
        )

        section = self.character_1001.reset_update_section(self.section)

        self.assertIsNone(section.is_success)
        self.assertEqual(section.last_error_message, "")

    def test_reset_2(self):
        """when section does not exist, then create it"""
        section = self.character_1001.reset_update_section(self.section)

        self.assertIsNone(section.is_success)
        self.assertEqual(section.last_error_message, "")

    def test_has_changed_1a(self):
        """When section exists, then return result from has_changed"""
        section = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=self.section,
            is_success=True,
            content_hash_1=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            self.character_1001.has_section_changed(
                section=self.section, content=self.content
            ),
            section.has_changed(self.content),
        )

    def test_has_changed_1b(self):
        """When section exists, then return result from has_changed"""
        section = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=self.section,
            is_success=True,
            content_hash_2=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            self.character_1001.has_section_changed(
                section=self.section, content=self.content, hash_num=2
            ),
            section.has_changed(self.content, hash_num=2),
        )

    def test_has_changed_1c(self):
        """When section exists, then return result from has_changed"""
        section = CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=self.section,
            is_success=True,
            content_hash_3=hashlib.md5(
                json.dumps(self.content).encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            self.character_1001.has_section_changed(
                section=self.section, content=self.content, hash_num=3
            ),
            section.has_changed(self.content, hash_num=3),
        )

    def test_has_changed_2(self):
        """When section does not exist, then return True"""
        self.assertTrue(
            self.character_1001.has_section_changed(
                section=self.section, content=self.content
            )
        )

    def test_is_updating_1(self):
        """When section exists, then return result from is_updating"""
        section = CharacterUpdateStatus.objects.create(
            character=self.character_1001, section=self.section, started_at=now()
        )
        self.assertEqual(
            self.character_1001.is_section_updating(section=self.section),
            section.is_updating,
        )

    def test_is_updating_2(self):
        """When section does not exist, then return False"""
        self.assertTrue(self.character_1001.is_section_updating(section=self.section))


@patch(MODELS_PATH + ".character.MEMBERAUDIT_UPDATE_STALE_RING_3", 640)
class TestCharacterIsUpdateSectionStale(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.section = Character.UpdateSection.ASSETS

    def setUp(self) -> None:
        self.character = create_memberaudit_character(1001)

    def test_recently_updated_successfully(self):
        """When section has been recently updated successfully then return False"""
        CharacterUpdateStatus.objects.create(
            character=self.character,
            section=self.section,
            is_success=True,
            started_at=now() - dt.timedelta(seconds=30),
            finished_at=now(),
        )
        self.assertFalse(self.character.is_update_section_stale(self.section))

    def test_recently_updated_unsuccessfully(self):
        """When section has been recently updated, but with errors then return True"""
        CharacterUpdateStatus.objects.create(
            character=self.character, section=self.section, is_success=False
        )
        self.assertTrue(self.character.is_update_section_stale(self.section))

    def test_update_long_ago(self):
        """When section has not been recently updated, then return True"""
        mocked_update_at = now() - dt.timedelta(hours=12)
        with patch("django.utils.timezone.now", Mock(return_value=mocked_update_at)):
            CharacterUpdateStatus.objects.create(
                character=self.character, section=self.section, is_success=True
            )
        self.assertTrue(self.character.is_update_section_stale(self.section))

    def test_does_not_exist(self):
        """When section does not exist, then return True"""
        self.assertTrue(self.character.is_update_section_stale(self.section))


class TestCharacterUserHasAccess(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)

    def test_user_owning_character_has_access(self):
        """
        when user is the owner of the character
        then return True
        """
        self.assertTrue(
            self.character_1001.user_has_access(
                self.character_1001.character_ownership.user
            )
        )

    def test_other_user_has_no_access(self):
        """
        when user is not the owner of the character
        and has no special permissions
        then return False
        """
        user_2 = AuthUtils.create_user("Lex Luthor")
        self.assertFalse(self.character_1001.user_has_access(user_2))

    def test_view_everything_1(self):
        """
        when user has view_everything permission and not characters_access
        then return False
        """
        user_3 = AuthUtils.create_user("Peter Parker")
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_everything", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))

    def test_view_everything_2(self):
        """
        when user has view_everything permission and characters_access
        then return True
        """
        user_3 = AuthUtils.create_user("Peter Parker")
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_everything", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        self.assertTrue(self.character_1001.user_has_access(user_3))

    def test_view_same_corporation_1a(self):
        """
        when user has view_same_corporation permission and not characters_access
        and is in the same corporation as the character owner (main)
        then return False
        """
        user_3, _ = create_user_from_evecharacter_with_access(1002)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))

    def test_view_same_corporation_1b(self):
        """
        when user has view_same_corporation permission and characters_access
        and is in the same corporation as the character owner (main)
        then return True
        """
        user_3, _ = create_user_from_evecharacter_with_access(1002)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        self.assertTrue(self.character_1001.user_has_access(user_3))

    def test_view_same_corporation_2a(self):
        """
        when user has view_same_corporation permission and not characters_access
        and is in the same corporation as the character owner (alt)
        then return False
        """
        user_3, _ = create_user_from_evecharacter_with_access(1002)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user_3
        )
        character_1103 = add_memberaudit_character_to_user(
            self.character_1001.character_ownership.user, 1103
        )
        self.assertFalse(character_1103.user_has_access(user_3))

    def test_view_same_corporation_2b(self):
        """
        when user has view_same_corporation permission and characters_access
        and is in the same corporation as the character owner (alt)
        then return True
        """
        user_3, _ = create_user_from_evecharacter_with_access(1002)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        character_1103 = add_memberaudit_character_to_user(
            self.character_1001.character_ownership.user, 1103
        )
        self.assertTrue(character_1103.user_has_access(user_3))

    def test_view_same_corporation_3(self):
        """
        when user has view_same_corporation permission and characters_access
        and is NOT in the same corporation as the character owner
        then return False
        """

        user_3, _ = create_user_from_evecharacter_with_access(1003)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))

    def test_view_same_alliance_1a(self):
        """
        when user has view_same_alliance permission and not characters_access
        and is in the same alliance as the character's owner (main)
        then return False
        """

        user_3, _ = create_user_from_evecharacter_with_access(1003)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))

    def test_view_same_alliance_1b(self):
        """
        when user has view_same_alliance permission and characters_access
        and is in the same alliance as the character's owner (main)
        then return True
        """

        user_3, _ = create_user_from_evecharacter_with_access(1003)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        self.assertTrue(self.character_1001.user_has_access(user_3))

    def test_view_same_alliance_2a(self):
        """
        when user has view_same_alliance permission and not characters_access
        and is in the same alliance as the character's owner (alt)
        then return False
        """

        user_3, _ = create_user_from_evecharacter_with_access(1003)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user_3
        )
        character_1103 = add_memberaudit_character_to_user(
            self.character_1001.character_ownership.user, 1103
        )
        self.assertFalse(character_1103.user_has_access(user_3))

    def test_view_same_alliance_2b(self):
        """
        when user has view_same_alliance permission and characters_access
        and is in the same alliance as the character's owner (alt)
        then return True
        """

        user_3, _ = create_user_from_evecharacter_with_access(1003)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        character_1103 = add_memberaudit_character_to_user(
            self.character_1001.character_ownership.user, 1103
        )
        self.assertTrue(character_1103.user_has_access(user_3))

    def test_view_same_alliance_3(self):
        """
        when user has view_same_alliance permission and characters_access
        and is NOT in the same alliance as the character owner
        then return False
        """
        user_3, _ = create_user_from_evecharacter_with_access(1101)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user_3
        )
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))

    def test_recruiter_access_1(self):
        """
        when user has recruiter permission
        and character is shared
        then return True
        """
        self.character_1001.is_shared = True
        self.character_1001.save()
        AuthUtils.add_permission_to_user_by_name(
            "memberaudit.share_characters", self.character_1001.character_ownership.user
        )
        user_3, _ = create_user_from_evecharacter_with_access(1101)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_shared_characters", user_3
        )
        self.assertTrue(self.character_1001.user_has_access(user_3))

    def test_recruiter_access_2(self):
        """
        when user has recruiter permission
        and character is NOT shared
        then return False
        """
        self.character_1001.is_shared = False
        self.character_1001.save()
        AuthUtils.add_permission_to_user_by_name(
            "memberaudit.share_characters", self.character_1001.character_ownership.user
        )
        user_3, _ = create_user_from_evecharacter_with_access(1101)
        user_3 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_shared_characters", user_3
        )
        self.assertFalse(self.character_1001.user_has_access(user_3))


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateContacts(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_update_contact_labels_1(self, mock_esi):
        """can create new contact labels from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contact_labels()
        self.assertEqual(self.character_1001.contact_labels.count(), 2)

        label = self.character_1001.contact_labels.get(label_id=1)
        self.assertEqual(label.name, "friend")

        label = self.character_1001.contact_labels.get(label_id=2)
        self.assertEqual(label.name, "pirate")

    def test_update_contact_labels_2(self, mock_esi):
        """can remove obsolete labels"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=99, name="Obsolete"
        )

        self.character_1001.update_contact_labels()
        self.assertEqual(
            {x.label_id for x in self.character_1001.contact_labels.all()}, {1, 2}
        )

    def test_update_contact_labels_3(self, mock_esi):
        """can update existing labels"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="Obsolete"
        )

        self.character_1001.update_contact_labels()
        self.assertEqual(
            {x.label_id for x in self.character_1001.contact_labels.all()}, {1, 2}
        )

        label = self.character_1001.contact_labels.get(label_id=1)
        self.assertEqual(label.name, "friend")

    def test_update_contact_labels_4(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contact_labels()
        label = self.character_1001.contact_labels.get(label_id=1)
        label.name = "foe"
        label.save()

        self.character_1001.update_contact_labels()

        self.assertEqual(self.character_1001.contact_labels.count(), 2)
        label = self.character_1001.contact_labels.get(label_id=1)
        self.assertEqual(label.name, "foe")

    def test_update_contact_labels_5(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contact_labels()
        label = self.character_1001.contact_labels.get(label_id=1)
        label.name = "foe"
        label.save()

        self.character_1001.update_contact_labels(force_update=True)

        self.assertEqual(self.character_1001.contact_labels.count(), 2)
        label = self.character_1001.contact_labels.get(label_id=1)
        self.assertEqual(label.name, "friend")

    def test_update_contacts_1(self, mock_esi):
        """can create contacts"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="friend"
        )
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=2, name="pirate"
        )

        self.character_1001.update_contacts()

        self.assertEqual(self.character_1001.contacts.count(), 2)

        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        self.assertEqual(obj.eve_entity.category, EveEntity.CATEGORY_CHARACTER)
        self.assertFalse(obj.is_blocked)
        self.assertTrue(obj.is_watched)
        self.assertEqual(obj.standing, -10)
        self.assertEqual({x.label_id for x in obj.labels.all()}, {2})

        obj = self.character_1001.contacts.get(eve_entity_id=2002)
        self.assertEqual(obj.eve_entity.category, EveEntity.CATEGORY_CORPORATION)
        self.assertFalse(obj.is_blocked)
        self.assertFalse(obj.is_watched)
        self.assertEqual(obj.standing, 5)
        self.assertEqual(obj.labels.count(), 0)

    def test_update_contacts_2(self, mock_esi):
        """can remove obsolete contacts"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="friend"
        )
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=2, name="pirate"
        )
        CharacterContact.objects.create(
            character=self.character_1001,
            eve_entity=EveEntity.objects.get(id=3101),
            standing=-5,
        )

        self.character_1001.update_contacts()

        self.assertEqual(
            {x.eve_entity_id for x in self.character_1001.contacts.all()}, {1101, 2002}
        )

    def test_update_contacts_3(self, mock_esi):
        """can update existing contacts"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=2, name="pirate"
        )
        my_label = CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="Dummy"
        )
        my_contact = CharacterContact.objects.create(
            character=self.character_1001,
            eve_entity=EveEntity.objects.get(id=1101),
            is_blocked=True,
            is_watched=False,
            standing=-5,
        )
        my_contact.labels.add(my_label)

        self.character_1001.update_contacts()

        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        self.assertEqual(obj.eve_entity.category, EveEntity.CATEGORY_CHARACTER)
        self.assertFalse(obj.is_blocked)
        self.assertTrue(obj.is_watched)
        self.assertEqual(obj.standing, -10)
        self.assertEqual({x.label_id for x in obj.labels.all()}, {2})

    def test_update_contacts_4(self, mock_esi):
        """when ESI data has not changed, then skip update"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="friend"
        )
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=2, name="pirate"
        )

        self.character_1001.update_contacts()
        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        obj.is_watched = False
        obj.save()

        self.character_1001.update_contacts()

        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        self.assertFalse(obj.is_watched)

    def test_update_contacts_5(self, mock_esi):
        """when ESI data has not changed and update is forced, then update"""
        mock_esi.client = esi_client_stub
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=1, name="friend"
        )
        CharacterContactLabel.objects.create(
            character=self.character_1001, label_id=2, name="pirate"
        )

        self.character_1001.update_contacts()
        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        obj.is_watched = False
        obj.save()

        self.character_1001.update_contacts(force_update=True)

        obj = self.character_1001.contacts.get(eve_entity_id=1101)
        self.assertTrue(obj.is_watched)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateContracts(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_1(self, mock_esi):
        """can create new courier contract"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contract_headers()
        self.assertSetEqual(
            set(self.character_1001.contracts.values_list("contract_id", flat=True)),
            {100000001, 100000002, 100000003},
        )

        obj = self.character_1001.contracts.get(contract_id=100000001)
        self.assertEqual(obj.contract_type, CharacterContract.TYPE_COURIER)
        self.assertEqual(obj.acceptor, EveEntity.objects.get(id=1101))
        self.assertEqual(obj.assignee, EveEntity.objects.get(id=2101))
        self.assertEqual(obj.availability, CharacterContract.AVAILABILITY_PERSONAL)
        self.assertIsNone(obj.buyout)
        self.assertEqual(float(obj.collateral), 550000000.0)
        self.assertEqual(obj.date_accepted, parse_datetime("2019-10-06T13:15:21Z"))
        self.assertEqual(obj.date_completed, parse_datetime("2019-10-07T13:15:21Z"))
        self.assertEqual(obj.date_expired, parse_datetime("2019-10-09T13:15:21Z"))
        self.assertEqual(obj.date_issued, parse_datetime("2019-10-02T13:15:21Z"))
        self.assertEqual(obj.days_to_complete, 3)
        self.assertEqual(obj.end_location, self.structure_1)
        self.assertFalse(obj.for_corporation)
        self.assertEqual(obj.issuer_corporation, EveEntity.objects.get(id=2001))
        self.assertEqual(obj.issuer, EveEntity.objects.get(id=1001))
        self.assertEqual(float(obj.price), 0.0)
        self.assertEqual(float(obj.reward), 500000000.0)
        self.assertEqual(obj.start_location, self.jita_44)
        self.assertEqual(obj.status, CharacterContract.STATUS_IN_PROGRESS)
        self.assertEqual(obj.title, "Test 1")
        self.assertEqual(obj.volume, 486000.0)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_2(self, mock_esi):
        """can create new item exchange contract"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contract_headers()
        obj = self.character_1001.contracts.get(contract_id=100000002)
        self.assertEqual(obj.contract_type, CharacterContract.TYPE_ITEM_EXCHANGE)
        self.assertEqual(float(obj.price), 270000000.0)
        self.assertEqual(obj.volume, 486000.0)
        self.assertEqual(obj.status, CharacterContract.STATUS_FINISHED)

        self.character_1001.update_contract_items(contract=obj)

        self.assertEqual(obj.items.count(), 2)

        item = obj.items.get(record_id=1)
        self.assertTrue(item.is_included)
        self.assertFalse(item.is_singleton)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.eve_type, EveType.objects.get(id=19540))

        item = obj.items.get(record_id=2)
        self.assertTrue(item.is_included)
        self.assertFalse(item.is_singleton)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.raw_quantity, -1)
        self.assertEqual(item.eve_type, EveType.objects.get(id=19551))

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_3(self, mock_esi):
        """can create new auction contract"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contract_headers()
        obj = self.character_1001.contracts.get(contract_id=100000003)
        self.assertEqual(obj.contract_type, CharacterContract.TYPE_AUCTION)
        self.assertEqual(float(obj.buyout), 200_000_000.0)
        self.assertEqual(float(obj.price), 20_000_000.0)
        self.assertEqual(obj.volume, 400.0)
        self.assertEqual(obj.status, CharacterContract.STATUS_OUTSTANDING)

        self.character_1001.update_contract_items(contract=obj)

        self.assertEqual(obj.items.count(), 1)
        item = obj.items.get(record_id=1)
        self.assertTrue(item.is_included)
        self.assertFalse(item.is_singleton)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.eve_type, EveType.objects.get(id=19540))

        self.character_1001.update_contract_bids(contract=obj)

        self.assertEqual(obj.bids.count(), 1)
        bid = obj.bids.get(bid_id=1)
        self.assertEqual(float(bid.amount), 1_000_000.23)
        self.assertEqual(bid.date_bid, parse_datetime("2017-01-01T10:10:10Z"))
        self.assertEqual(bid.bidder, EveEntity.objects.get(id=1101))

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_4(self, mock_esi):
        """old contracts must be kept"""
        mock_esi.client = esi_client_stub

        CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=190000001,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_COURIER,
            assignee=EveEntity.objects.get(id=1002),
            date_issued=now() - dt.timedelta(days=60),
            date_expired=now() - dt.timedelta(days=30),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_IN_PROGRESS,
            start_location=self.jita_44,
            end_location=self.structure_1,
            title="Old contract",
        )

        self.character_1001.update_contract_headers()
        self.assertEqual(self.character_1001.contracts.count(), 4)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_5(self, mock_esi):
        """Existing contracts are updated"""
        mock_esi.client = esi_client_stub

        CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=100000001,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_COURIER,
            assignee=EveEntity.objects.get(id=2101),
            date_issued=parse_datetime("2019-10-02T13:15:21Z"),
            date_expired=parse_datetime("2019-10-09T13:15:21Z"),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_OUTSTANDING,
            start_location=self.jita_44,
            end_location=self.structure_1,
            title="Test 1",
            collateral=550000000,
            reward=500000000,
            volume=486000,
            days_to_complete=3,
        )

        self.character_1001.update_contract_headers()

        obj = self.character_1001.contracts.get(contract_id=100000001)
        self.assertEqual(obj.contract_type, CharacterContract.TYPE_COURIER)
        self.assertEqual(obj.acceptor, EveEntity.objects.get(id=1101))
        self.assertEqual(obj.assignee, EveEntity.objects.get(id=2101))
        self.assertEqual(obj.availability, CharacterContract.AVAILABILITY_PERSONAL)
        self.assertIsNone(obj.buyout)
        self.assertEqual(float(obj.collateral), 550000000.0)
        self.assertEqual(obj.date_accepted, parse_datetime("2019-10-06T13:15:21Z"))
        self.assertEqual(obj.date_completed, parse_datetime("2019-10-07T13:15:21Z"))
        self.assertEqual(obj.date_expired, parse_datetime("2019-10-09T13:15:21Z"))
        self.assertEqual(obj.date_issued, parse_datetime("2019-10-02T13:15:21Z"))
        self.assertEqual(obj.days_to_complete, 3)
        self.assertEqual(obj.end_location, self.structure_1)
        self.assertFalse(obj.for_corporation)
        self.assertEqual(obj.issuer_corporation, EveEntity.objects.get(id=2001))
        self.assertEqual(obj.issuer, EveEntity.objects.get(id=1001))
        self.assertEqual(float(obj.reward), 500000000.0)
        self.assertEqual(obj.start_location, self.jita_44)
        self.assertEqual(obj.status, CharacterContract.STATUS_IN_PROGRESS)
        self.assertEqual(obj.title, "Test 1")
        self.assertEqual(obj.volume, 486000.0)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_6(self, mock_esi):
        """can add new bids to auction contract"""
        mock_esi.client = esi_client_stub
        contract = CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=100000003,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_AUCTION,
            assignee=EveEntity.objects.get(id=2101),
            date_issued=parse_datetime("2019-10-02T13:15:21Z"),
            date_expired=parse_datetime("2019-10-09T13:15:21Z"),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_OUTSTANDING,
            start_location=self.jita_44,
            end_location=self.jita_44,
            buyout=200_000_000,
            price=20_000_000,
            volume=400,
        )
        CharacterContractBid.objects.create(
            contract=contract,
            bid_id=2,
            amount=21_000_000,
            bidder=EveEntity.objects.get(id=1003),
            date_bid=now(),
        )

        self.character_1001.update_contract_headers()
        obj = self.character_1001.contracts.get(contract_id=100000003)
        self.character_1001.update_contract_bids(contract=obj)

        self.assertEqual(obj.bids.count(), 2)

        bid = obj.bids.get(bid_id=1)
        self.assertEqual(float(bid.amount), 1_000_000.23)
        self.assertEqual(bid.date_bid, parse_datetime("2017-01-01T10:10:10Z"))
        self.assertEqual(bid.bidder, EveEntity.objects.get(id=1101))

        bid = obj.bids.get(bid_id=2)
        self.assertEqual(float(bid.amount), 21_000_000)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_7(self, mock_esi):
        """when contract list from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_contract_headers()
        obj = self.character_1001.contracts.get(contract_id=100000001)
        obj.status = CharacterContract.STATUS_FINISHED
        obj.save()

        self.character_1001.update_contract_headers()

        obj = self.character_1001.contracts.get(contract_id=100000001)
        self.assertEqual(obj.status, CharacterContract.STATUS_FINISHED)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_contracts_8(self, mock_esi):
        """
        when contract list from ESI has not changed and update is forced, then update
        """
        mock_esi.client = esi_client_stub

        self.character_1001.update_contract_headers()
        obj = self.character_1001.contracts.get(contract_id=100000001)
        obj.status = CharacterContract.STATUS_FINISHED
        obj.save()

        self.character_1001.update_contract_headers(force_update=True)

        obj = self.character_1001.contracts.get(contract_id=100000001)
        self.assertEqual(obj.status, CharacterContract.STATUS_IN_PROGRESS)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 10)
    def test_update_contracts_9(self, mock_esi):
        """when retention limit is set, then only create contracts younger than limit"""
        mock_esi.client = esi_client_stub

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2019, 10, 21, 1, 15), UTC)
            self.character_1001.update_contract_headers()

        self.assertSetEqual(
            set(self.character_1001.contracts.values_list("contract_id", flat=True)),
            {100000002, 100000003},
        )

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 15)
    def test_update_contracts_10(self, mock_esi):
        """when retention limit is set,
        then remove existing contracts older than limit
        """
        mock_esi.client = esi_client_stub
        CharacterContract.objects.create(
            character=self.character_1001,
            contract_id=100000004,
            availability=CharacterContract.AVAILABILITY_PERSONAL,
            contract_type=CharacterContract.TYPE_COURIER,
            assignee=EveEntity.objects.get(id=2101),
            date_issued=parse_datetime("2019-09-02T13:15:21Z"),
            date_expired=parse_datetime("2019-09-09T13:15:21Z"),
            for_corporation=False,
            issuer=EveEntity.objects.get(id=1001),
            issuer_corporation=EveEntity.objects.get(id=2001),
            status=CharacterContract.STATUS_OUTSTANDING,
            start_location=self.jita_44,
            end_location=self.structure_1,
            title="This contract is too old",
            collateral=550000000,
            reward=500000000,
            volume=486000,
            days_to_complete=3,
        )

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2019, 10, 21, 1, 15), UTC)
            self.character_1001.update_contract_headers()

        self.assertSetEqual(
            set(self.character_1001.contracts.values_list("contract_id", flat=True)),
            {100000001, 100000002, 100000003},
        )


@patch(MANAGERS_PATH + ".sections.eve_xml_to_html")
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateCharacterDetails(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create(self, mock_esi, mock_eve_xml_to_html):
        """can create from scratch"""
        mock_esi.client = esi_client_stub
        mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)

        self.character_1001.update_character_details()
        self.assertEqual(self.character_1001.details.eve_ancestry.id, 11)
        self.assertEqual(
            self.character_1001.details.birthday, parse_datetime("2015-03-24T11:37:00Z")
        )
        self.assertEqual(self.character_1001.details.eve_bloodline_id, 1)
        self.assertEqual(self.character_1001.details.corporation, self.corporation_2001)
        self.assertEqual(self.character_1001.details.description, "Scio me nihil scire")
        self.assertEqual(
            self.character_1001.details.gender, CharacterDetails.GENDER_MALE
        )
        self.assertEqual(self.character_1001.details.name, "Bruce Wayne")
        self.assertEqual(self.character_1001.details.eve_race.id, 1)
        self.assertEqual(
            self.character_1001.details.title, "All round pretty awesome guy"
        )
        self.assertTrue(mock_eve_xml_to_html.called)

    def test_update(self, mock_esi, mock_eve_xml_to_html):
        """can update existing data"""
        mock_esi.client = esi_client_stub
        mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)
        CharacterDetails.objects.create(
            character=self.character_1001,
            birthday=now(),
            corporation=self.corporation_2002,
            description="Change me",
            eve_bloodline_id=1,
            eve_race_id=1,
            name="Change me also",
        )

        self.character_1001.update_character_details()
        self.character_1001.details.refresh_from_db()
        self.assertEqual(self.character_1001.details.eve_ancestry_id, 11)
        self.assertEqual(
            self.character_1001.details.birthday, parse_datetime("2015-03-24T11:37:00Z")
        )
        self.assertEqual(self.character_1001.details.eve_bloodline_id, 1)
        self.assertEqual(self.character_1001.details.corporation, self.corporation_2001)
        self.assertEqual(self.character_1001.details.description, "Scio me nihil scire")
        self.assertEqual(
            self.character_1001.details.gender, CharacterDetails.GENDER_MALE
        )
        self.assertEqual(self.character_1001.details.name, "Bruce Wayne")
        self.assertEqual(self.character_1001.details.eve_race.id, 1)
        self.assertEqual(
            self.character_1001.details.title, "All round pretty awesome guy"
        )
        self.assertTrue(mock_eve_xml_to_html.called)

    def test_skip_update_1(self, mock_esi, mock_eve_xml_to_html):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub
        mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)

        self.character_1001.update_character_details()
        self.character_1001.details.name = "John Doe"
        self.character_1001.details.save()

        self.character_1001.update_character_details()
        self.character_1001.details.refresh_from_db()
        self.assertEqual(self.character_1001.details.name, "John Doe")

    def test_skip_update_2(self, mock_esi, mock_eve_xml_to_html):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub
        mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)

        self.character_1001.update_character_details()
        self.character_1001.details.name = "John Doe"
        self.character_1001.details.save()

        self.character_1001.update_character_details(force_update=True)
        self.character_1001.details.refresh_from_db()
        self.assertEqual(self.character_1001.details.name, "Bruce Wayne")

    # @patch(MANAGERS_PATH + ".sections.get_or_create_esi_or_none")
    # def test_esi_ancestry_bug(
    #     self, mock_get_or_create_esi_or_none, mock_esi, mock_eve_xml_to_html
    # ):
    #     """when esi ancestry endpoint returns http error then ignore it and carry on"""

    #     def my_get_or_create_esi_or_none(prop_name: str, dct: dict, Model: type):
    #         if issubclass(Model, EveAncestry):
    #             raise HTTPInternalServerError(
    #                 response=BravadoResponseStub(500, "Test exception")
    #             )
    #         return get_or_create_esi_or_none(prop_name=prop_name, dct=dct, Model=Model)

    #     mock_esi.client = esi_client_stub
    #     mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)
    #     mock_get_or_create_esi_or_none.side_effect = my_get_or_create_esi_or_none

    #     self.character_1001.update_character_details()
    #     self.assertIsNone(self.character_1001.details.eve_ancestry)
    #     self.assertEqual(
    #         self.character_1001.details.birthday, parse_datetime("2015-03-24T11:37:00Z")
    #     )
    #     self.assertEqual(self.character_1001.details.eve_bloodline_id, 1)
    #     self.assertEqual(self.character_1001.details.corporation, self.corporation_2001)
    #     self.assertEqual(self.character_1001.details.description, "Scio me nihil scire")
    #     self.assertEqual(
    #         self.character_1001.details.gender, CharacterDetails.GENDER_MALE
    #     )
    #     self.assertEqual(self.character_1001.details.name, "Bruce Wayne")
    #     self.assertEqual(self.character_1001.details.eve_race.id, 1)
    #     self.assertEqual(
    #         self.character_1001.details.title, "All round pretty awesome guy"
    #     )
    #     self.assertTrue(mock_eve_xml_to_html.called)


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateCorporationHistory(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create(self, mock_esi):
        """can create corporation history from scratch"""
        mock_esi.client = esi_client_stub
        self.character_1001.update_corporation_history()
        self.assertEqual(self.character_1001.corporation_history.count(), 2)

        obj = self.character_1001.corporation_history.get(record_id=500)
        self.assertEqual(obj.corporation, self.corporation_2001)
        self.assertTrue(obj.is_deleted)
        self.assertEqual(obj.start_date, parse_datetime("2016-06-26T20:00:00Z"))

        obj = self.character_1001.corporation_history.get(record_id=501)
        self.assertEqual(obj.corporation, self.corporation_2002)
        self.assertFalse(obj.is_deleted)
        self.assertEqual(obj.start_date, parse_datetime("2016-07-26T20:00:00Z"))

    def test_update_1(self, mock_esi):
        """can update existing corporation history"""
        mock_esi.client = esi_client_stub
        self.character_1001.corporation_history.create(
            record_id=500, corporation=self.corporation_2002, start_date=now()
        )

        self.character_1001.update_corporation_history()
        self.assertEqual(self.character_1001.corporation_history.count(), 2)

        obj = self.character_1001.corporation_history.get(record_id=500)
        self.assertEqual(obj.corporation, self.corporation_2001)
        self.assertTrue(obj.is_deleted)
        self.assertEqual(obj.start_date, parse_datetime("2016-06-26T20:00:00Z"))

    def test_update_2(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_corporation_history()
        obj = self.character_1001.corporation_history.get(record_id=500)
        obj.corporation = self.corporation_2002
        obj.save()

        self.character_1001.update_corporation_history()
        obj = self.character_1001.corporation_history.get(record_id=500)
        self.assertEqual(obj.corporation, self.corporation_2002)

    def test_update_3(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_corporation_history()
        obj = self.character_1001.corporation_history.get(record_id=500)
        obj.corporation = self.corporation_2002
        obj.save()

        self.character_1001.update_corporation_history(force_update=True)

        obj = self.character_1001.corporation_history.get(record_id=500)
        self.assertEqual(obj.corporation, self.corporation_2001)


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateImplants(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_update_implants_1(self, mock_esi):
        """can create implants from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_implants()
        self.assertEqual(self.character_1001.implants.count(), 3)
        self.assertSetEqual(
            set(self.character_1001.implants.values_list("eve_type_id", flat=True)),
            {19540, 19551, 19553},
        )

    def test_update_implants_2(self, mock_esi):
        """can deal with no implants returned from ESI"""
        mock_esi.client = esi_client_stub

        self.character_1002.update_implants()
        self.assertEqual(self.character_1002.implants.count(), 0)

    def test_update_implants_3(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_implants()
        self.character_1001.implants.get(eve_type_id=19540).delete()

        self.character_1001.update_implants()
        self.assertFalse(
            self.character_1001.implants.filter(eve_type_id=19540).exists()
        )

    def test_update_implants_4(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_implants()
        self.character_1001.implants.get(eve_type_id=19540).delete()

        self.character_1001.update_implants(force_update=True)
        self.assertTrue(self.character_1001.implants.filter(eve_type_id=19540).exists())


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateJumpClones(TestCharacterUpdateBase):
    def test_update_jump_clones_1(self, mock_esi):
        """can update jump clones with implants"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_jump_clones()
        self.assertEqual(self.character_1001.jump_clones.count(), 1)

        obj = self.character_1001.jump_clones.get(jump_clone_id=12345)
        self.assertEqual(obj.location, self.jita_44)
        self.assertEqual(
            {x for x in obj.implants.values_list("eve_type", flat=True)},
            {19540, 19551, 19553},
        )

    def test_update_jump_clones_2(self, mock_esi):
        """can update jump clones without implants"""
        mock_esi.client = esi_client_stub

        self.character_1002.update_jump_clones()
        self.assertEqual(self.character_1002.jump_clones.count(), 1)

        obj = self.character_1002.jump_clones.get(jump_clone_id=12345)
        self.assertEqual(obj.location, self.jita_44)
        self.assertEqual(obj.implants.count(), 0)

    def test_skip_update_1(self, mock_esi):
        """when ESI data has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_jump_clones()
        obj = self.character_1001.jump_clones.get(jump_clone_id=12345)
        obj.location = self.structure_1
        obj.save()

        self.character_1001.update_jump_clones()

        obj = self.character_1001.jump_clones.get(jump_clone_id=12345)
        self.assertEqual(obj.location, self.structure_1)

    def test_skip_update_2(self, mock_esi):
        """when ESI data has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_jump_clones()
        obj = self.character_1001.jump_clones.get(jump_clone_id=12345)
        obj.location = self.structure_1
        obj.save()

        self.character_1001.update_jump_clones(force_update=True)

        obj = self.character_1001.jump_clones.get(jump_clone_id=12345)
        self.assertEqual(obj.location, self.jita_44)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateMails(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_update_mailing_lists_1(self, mock_esi):
        """can create new mailing lists from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mailing_lists()

        self.assertSetEqual(
            set(MailEntity.objects.values_list("id", flat=True)), {9001, 9002}
        )
        self.assertSetEqual(
            set(self.character_1001.mailing_lists.values_list("id", flat=True)),
            {9001, 9002},
        )

        obj = MailEntity.objects.get(id=9001)
        self.assertEqual(obj.name, "Dummy 1")

        obj = MailEntity.objects.get(id=9002)
        self.assertEqual(obj.name, "Dummy 2")

    def test_update_mailing_lists_2(self, mock_esi):
        """does not remove obsolete mailing lists"""
        mock_esi.client = esi_client_stub
        MailEntity.objects.create(
            id=5, category=MailEntity.Category.MAILING_LIST, name="Obsolete"
        )

        self.character_1001.update_mailing_lists()

        self.assertSetEqual(
            set(MailEntity.objects.values_list("id", flat=True)), {9001, 9002, 5}
        )
        self.assertSetEqual(
            set(self.character_1001.mailing_lists.values_list("id", flat=True)),
            {9001, 9002},
        )

    def test_update_mailing_lists_3(self, mock_esi):
        """updates existing mailing lists"""
        mock_esi.client = esi_client_stub
        MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Update me"
        )

        self.character_1001.update_mailing_lists()

        self.assertSetEqual(
            set(MailEntity.objects.values_list("id", flat=True)), {9001, 9002}
        )
        self.assertSetEqual(
            set(self.character_1001.mailing_lists.values_list("id", flat=True)),
            {9001, 9002},
        )
        obj = MailEntity.objects.get(id=9001)
        self.assertEqual(obj.name, "Dummy 1")

    def test_update_mailing_lists_4(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mailing_lists()
        obj = MailEntity.objects.get(id=9001)
        obj.name = "Extravaganza"
        obj.save()
        self.character_1001.mailing_lists.clear()

        self.character_1001.update_mailing_lists()
        obj = MailEntity.objects.get(id=9001)
        self.assertEqual(obj.name, "Extravaganza")
        self.assertSetEqual(
            set(self.character_1001.mailing_lists.values_list("id", flat=True)), set()
        )

    def test_update_mailing_lists_5(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mailing_lists()
        obj = MailEntity.objects.get(id=9001)
        obj.name = "Extravaganza"
        obj.save()

        self.character_1001.update_mailing_lists(force_update=True)
        obj = MailEntity.objects.get(id=9001)
        self.assertEqual(obj.name, "Dummy 1")

    def test_update_mail_labels_1(self, mock_esi):
        """can create from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mail_labels()

        self.assertEqual(self.character_1001.unread_mail_count.total, 5)
        self.assertSetEqual(
            set(self.character_1001.mail_labels.values_list("label_id", flat=True)),
            {3, 17},
        )

        obj = self.character_1001.mail_labels.get(label_id=3)
        self.assertEqual(obj.name, "PINK")
        self.assertEqual(obj.unread_count, 4)
        self.assertEqual(obj.color, "#660066")

        obj = self.character_1001.mail_labels.get(label_id=17)
        self.assertEqual(obj.name, "WHITE")
        self.assertEqual(obj.unread_count, 1)
        self.assertEqual(obj.color, "#ffffff")

    def test_update_mail_labels_2(self, mock_esi):
        """will remove obsolete labels"""
        mock_esi.client = esi_client_stub
        CharacterMailLabel.objects.create(
            character=self.character_1001, label_id=666, name="Obsolete"
        )

        self.character_1001.update_mail_labels()

        self.assertSetEqual(
            set(self.character_1001.mail_labels.values_list("label_id", flat=True)),
            {3, 17},
        )

    def test_update_mail_labels_3(self, mock_esi):
        """will update existing labels"""
        mock_esi.client = esi_client_stub
        CharacterMailLabel.objects.create(
            character=self.character_1001,
            label_id=3,
            name="Update me",
            unread_count=0,
            color=0,
        )

        self.character_1001.update_mail_labels()

        self.assertSetEqual(
            set(self.character_1001.mail_labels.values_list("label_id", flat=True)),
            {3, 17},
        )

        obj = self.character_1001.mail_labels.get(label_id=3)
        self.assertEqual(obj.name, "PINK")
        self.assertEqual(obj.unread_count, 4)
        self.assertEqual(obj.color, "#660066")

    def test_update_mail_labels_4(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mail_labels()
        obj = self.character_1001.mail_labels.get(label_id=3)
        obj.name = "MAGENTA"
        obj.save()

        self.character_1001.update_mail_labels()

        obj = self.character_1001.mail_labels.get(label_id=3)
        self.assertEqual(obj.name, "MAGENTA")

    def test_update_mail_labels_5(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_mail_labels()
        obj = self.character_1001.mail_labels.get(label_id=3)
        obj.name = "MAGENTA"
        obj.save()

        self.character_1001.update_mail_labels(force_update=True)

        obj = self.character_1001.mail_labels.get(label_id=3)
        self.assertEqual(obj.name, "PINK")

    @staticmethod
    def stub_eve_entity_get_or_create_esi(id, *args, **kwargs):
        """will return EveEntity if it exists else None, False"""
        try:
            obj = EveEntity.objects.get(id=id)
            return obj, True
        except EveEntity.DoesNotExist:
            return None, False

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_1(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """can create new mail from scratch"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        self.character_1001.update_mailing_lists()
        self.character_1001.update_mail_labels()
        self.character_1001.update_mail_headers()
        self.assertSetEqual(
            set(self.character_1001.mails.values_list("mail_id", flat=True)),
            {1, 2, 3},
        )

        obj = self.character_1001.mails.get(mail_id=1)
        self.assertEqual(obj.sender.id, 1002)
        self.assertTrue(obj.is_read)
        self.assertEqual(obj.subject, "Mail 1")
        self.assertEqual(obj.timestamp, parse_datetime("2015-09-05T16:07:00Z"))
        self.assertFalse(obj.body)
        self.assertTrue(obj.recipients.filter(id=1001).exists())
        self.assertTrue(obj.recipients.filter(id=9001).exists())
        self.assertSetEqual(set(obj.labels.values_list("label_id", flat=True)), {3})

        obj = self.character_1001.mails.get(mail_id=2)
        self.assertEqual(obj.sender_id, 9001)
        self.assertFalse(obj.is_read)
        self.assertEqual(obj.subject, "Mail 2")
        self.assertEqual(obj.timestamp, parse_datetime("2015-09-10T18:07:00Z"))
        self.assertFalse(obj.body)
        self.assertSetEqual(set(obj.labels.values_list("label_id", flat=True)), {3})

        obj = self.character_1001.mails.get(mail_id=3)
        self.assertEqual(obj.sender_id, 1002)
        self.assertTrue(obj.recipients.filter(id=9003).exists())
        self.assertEqual(obj.timestamp, parse_datetime("2015-09-20T12:07:00Z"))

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_2(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """can update existing mail"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        sender, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1002)
        mail = CharacterMail.objects.create(
            character=self.character_1001,
            mail_id=1,
            sender=sender,
            subject="Mail 1",
            timestamp=parse_datetime("2015-09-05T16:07:00Z"),
            is_read=False,  # to be updated
        )
        recipient_1, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1001)
        recipient_2 = MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Dummy 2"
        )
        mail.recipients.set([recipient_1, recipient_2])

        self.character_1001.update_mailing_lists()
        self.character_1001.update_mail_labels()
        label = self.character_1001.mail_labels.get(label_id=17)
        mail.labels.add(label)  # to be updated

        self.character_1001.update_mail_headers()
        self.assertSetEqual(
            set(self.character_1001.mails.values_list("mail_id", flat=True)),
            {1, 2, 3},
        )

        obj = self.character_1001.mails.get(mail_id=1)
        self.assertEqual(obj.sender_id, 1002)
        self.assertTrue(obj.is_read)
        self.assertEqual(obj.subject, "Mail 1")
        self.assertEqual(obj.timestamp, parse_datetime("2015-09-05T16:07:00Z"))
        self.assertFalse(obj.body)
        self.assertTrue(obj.recipients.filter(id=1001).exists())
        self.assertTrue(obj.recipients.filter(id=9001).exists())
        self.assertSetEqual(set(obj.labels.values_list("label_id", flat=True)), {3})

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_3(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """when ESI data is unchanged, then skip update"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        self.character_1001.update_mailing_lists()
        self.character_1001.update_mail_labels()
        self.character_1001.update_mail_headers()
        obj = self.character_1001.mails.get(mail_id=1)
        obj.is_read = False
        obj.save()

        self.character_1001.update_mail_headers()

        obj = self.character_1001.mails.get(mail_id=1)
        self.assertFalse(obj.is_read)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_4(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """when ESI data is unchanged and update forced, then do update"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        self.character_1001.update_mailing_lists()
        self.character_1001.update_mail_labels()
        self.character_1001.update_mail_headers()
        obj = self.character_1001.mails.get(mail_id=1)
        obj.is_read = False
        obj.save()

        self.character_1001.update_mail_headers(force_update=True)

        obj = self.character_1001.mails.get(mail_id=1)
        self.assertTrue(obj.is_read)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 15)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_6(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """when data retention limit is set, then only fetch mails within that limit"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2015, 9, 20, 20, 5), UTC)
            self.character_1001.update_mailing_lists()
            self.character_1001.update_mail_labels()
            self.character_1001.update_mail_headers()

        self.assertSetEqual(
            set(self.character_1001.mails.values_list("mail_id", flat=True)),
            {2, 3},
        )

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 15)
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".sections.EveEntity.objects.get_or_create_esi")
    def test_update_mail_headers_7(
        self, mock_eve_entity, mock_fetch_esi_status, mock_esi
    ):
        """when data retention limit is set, then remove old data beyond that limit"""
        mock_esi.client = esi_client_stub
        mock_eve_entity.side_effect = self.stub_eve_entity_get_or_create_esi
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        sender, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1002)
        CharacterMail.objects.create(
            character=self.character_1001,
            mail_id=99,
            sender=sender,
            subject="Mail Old",
            timestamp=parse_datetime("2015-09-02T14:02:00Z"),
            is_read=False,
        )

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2015, 9, 20, 20, 5), UTC)
            self.character_1001.update_mailing_lists()
            self.character_1001.update_mail_labels()
            self.character_1001.update_mail_headers()

        self.assertSetEqual(
            set(self.character_1001.mails.values_list("mail_id", flat=True)),
            {2, 3},
        )

    def test_should_update_existing_mail_body(self, mock_esi):
        # given
        mock_esi.client = esi_client_stub
        sender, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1002)
        mail = CharacterMail.objects.create(
            character=self.character_1001,
            mail_id=1,
            sender=sender,
            subject="Mail 1",
            body="Update me",
            is_read=False,
            timestamp=parse_datetime("2015-09-30T16:07:00Z"),
        )
        recipient_1001, _ = MailEntity.objects.update_or_create_from_eve_entity_id(
            id=1001
        )
        recipient_9001 = MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Dummy 2"
        )
        mail.recipients.add(recipient_1001, recipient_9001)
        # when
        self.character_1001.update_mail_body(mail)
        # then
        obj = self.character_1001.mails.get(mail_id=1)
        self.assertEqual(obj.body, "blah blah blah")

    @patch(MODELS_PATH + ".character.eve_xml_to_html")
    def test_should_update_mail_body_from_scratch(self, mock_eve_xml_to_html, mock_esi):
        # given
        mock_esi.client = esi_client_stub
        mock_eve_xml_to_html.side_effect = lambda x: eve_xml_to_html(x)
        sender, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1002)
        mail = CharacterMail.objects.create(
            character=self.character_1001,
            mail_id=2,
            sender=sender,
            subject="Mail 1",
            is_read=False,
            timestamp=parse_datetime("2015-09-30T16:07:00Z"),
        )
        recipient_1, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1001)
        mail.recipients.add(recipient_1)
        # when
        self.character_1001.update_mail_body(mail)
        # then
        obj = self.character_1001.mails.get(mail_id=2)
        self.assertTrue(obj.body)
        self.assertTrue(mock_eve_xml_to_html.called)

    def test_should_delete_mail_header_when_fetching_body_returns_404(self, mock_esi):
        # given
        mock_esi.client.Mail.get_characters_character_id_mail_mail_id.side_effect = (
            HTTPNotFound(response=BravadoResponseStub(404, "Test"))
        )
        sender, _ = MailEntity.objects.update_or_create_from_eve_entity_id(id=1002)
        mail = CharacterMail.objects.create(
            character=self.character_1001,
            mail_id=1,
            sender=sender,
            subject="Mail 1",
            is_read=False,
            timestamp=parse_datetime("2015-09-30T16:07:00Z"),
        )
        recipient_1001, _ = MailEntity.objects.update_or_create_from_eve_entity_id(
            id=1001
        )
        recipient_9001 = MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Dummy 2"
        )
        mail.recipients.add(recipient_1001, recipient_9001)
        # when
        self.character_1001.update_mail_body(mail)
        # then
        self.assertFalse(self.character_1001.mails.filter(mail_id=1).exists())


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateLoyalty(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create(self, mock_esi):
        """can create from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_loyalty()
        self.assertEqual(self.character_1001.loyalty_entries.count(), 1)

        obj = self.character_1001.loyalty_entries.get(corporation_id=2002)
        self.assertEqual(obj.loyalty_points, 100)

    def test_update(self, mock_esi):
        """can update existing loyalty"""
        mock_esi.client = esi_client_stub
        self.character_1001.loyalty_entries.create(
            corporation=self.corporation_2001, loyalty_points=200
        )

        self.character_1001.update_loyalty()
        self.assertEqual(self.character_1001.loyalty_entries.count(), 1)

        obj = self.character_1001.loyalty_entries.get(corporation=self.corporation_2002)
        self.assertEqual(obj.loyalty_points, 100)

    def test_skip_update_1(self, mock_esi):
        """when data from ESI has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_loyalty()
        obj = self.character_1001.loyalty_entries.get(corporation=self.corporation_2002)
        obj.loyalty_points = 200
        obj.save()
        self.character_1001.update_loyalty()

        obj = self.character_1001.loyalty_entries.get(corporation=self.corporation_2002)
        self.assertEqual(obj.loyalty_points, 200)

    def test_skip_update_2(self, mock_esi):
        """when data from ESI has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_loyalty()
        obj = self.character_1001.loyalty_entries.get(corporation=self.corporation_2002)
        obj.loyalty_points = 200
        obj.save()

        self.character_1001.update_loyalty(force_update=True)

        obj = self.character_1001.loyalty_entries.get(corporation=self.corporation_2002)
        self.assertEqual(obj.loyalty_points, 100)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateLocation(TestCharacterUpdateBase):
    def test_update_location_1(self, mock_esi):
        mock_esi.client = esi_client_stub

        self.character_1001.update_location()
        self.assertEqual(self.character_1001.location.eve_solar_system, self.jita)
        self.assertEqual(self.character_1001.location.location, self.jita_44)

    def test_update_location_2(self, mock_esi):
        mock_esi.client = esi_client_stub

        self.character_1002.update_location()
        self.assertEqual(self.character_1002.location.eve_solar_system, self.amamake)
        self.assertEqual(self.character_1002.location.location, self.structure_1)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateOnlineStatus(TestCharacterUpdateBase):
    def test_update_online_status(self, mock_esi):
        mock_esi.client = esi_client_stub

        self.character_1001.update_online_status()
        self.assertEqual(
            self.character_1001.online_status.last_login,
            parse_datetime("2017-01-02T03:04:05Z"),
        )
        self.assertEqual(
            self.character_1001.online_status.last_logout,
            parse_datetime("2017-01-02T04:05:06Z"),
        )
        self.assertEqual(self.character_1001.online_status.logins, 9001)


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateShip(TestCharacterUpdateBase):
    def test_should_update_all_fields(self, mock_esi):
        # given
        mock_esi.client = esi_client_stub
        # when
        self.character_1001.update_ship()
        # then
        self.assertEqual(self.character_1001.ship.eve_type, EveType.objects.get(id=603))
        self.assertEqual(self.character_1001.ship.name, "Shooter Boy")


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateSkills(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_update_skills_1(self, mock_esi):
        """can create new skills"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_skills()
        self.assertEqual(self.character_1001.skillpoints.total, 30_000)
        self.assertEqual(self.character_1001.skillpoints.unallocated, 1_000)

        self.assertSetEqual(
            set(self.character_1001.skills.values_list("eve_type_id", flat=True)),
            {24311, 24312},
        )

        skill = self.character_1001.skills.get(eve_type_id=24311)
        self.assertEqual(skill.active_skill_level, 3)
        self.assertEqual(skill.skillpoints_in_skill, 20_000)
        self.assertEqual(skill.trained_skill_level, 4)

        skill = self.character_1001.skills.get(eve_type_id=24312)
        self.assertEqual(skill.active_skill_level, 1)
        self.assertEqual(skill.skillpoints_in_skill, 10_000)
        self.assertEqual(skill.trained_skill_level, 1)

    def test_update_skills_2(self, mock_esi):
        """can update existing skills"""
        mock_esi.client = esi_client_stub

        CharacterSkill.objects.create(
            character=self.character_1001,
            eve_type=EveType.objects.get(id=24311),
            active_skill_level=1,
            skillpoints_in_skill=1,
            trained_skill_level=1,
        )

        self.character_1001.update_skills()

        self.assertEqual(self.character_1001.skills.count(), 2)
        skill = self.character_1001.skills.get(eve_type_id=24311)
        self.assertEqual(skill.active_skill_level, 3)
        self.assertEqual(skill.skillpoints_in_skill, 20_000)
        self.assertEqual(skill.trained_skill_level, 4)

    def test_update_skills_3(self, mock_esi):
        """can delete obsolete skills"""
        mock_esi.client = esi_client_stub

        CharacterSkill.objects.create(
            character=self.character_1001,
            eve_type=EveType.objects.get(id=20185),
            active_skill_level=1,
            skillpoints_in_skill=1,
            trained_skill_level=1,
        )

        self.character_1001.update_skills()

        self.assertSetEqual(
            set(self.character_1001.skills.values_list("eve_type_id", flat=True)),
            {24311, 24312},
        )

    def test_update_skills_4(self, mock_esi):
        """when ESI info has not changed, then do not update local data"""
        mock_esi.client = esi_client_stub

        self.character_1001.reset_update_section(Character.UpdateSection.SKILLS)
        self.character_1001.update_skills()
        skill = self.character_1001.skills.get(eve_type_id=24311)
        skill.active_skill_level = 4
        skill.save()
        self.character_1001.update_skills()
        skill.refresh_from_db()
        self.assertEqual(skill.active_skill_level, 4)

    def test_update_skills_5(self, mock_esi):
        """when ESI info has not changed and update forced, then update local data"""
        mock_esi.client = esi_client_stub

        self.character_1001.reset_update_section(Character.UpdateSection.SKILLS)
        self.character_1001.update_skills()
        skill = self.character_1001.skills.get(eve_type_id=24311)
        skill.active_skill_level = 4
        skill.save()

        self.character_1001.update_skills(force_update=True)

        skill = self.character_1001.skills.get(eve_type_id=24311)
        self.assertEqual(skill.active_skill_level, 3)


class TestCharacterUpdateSkillSets(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character = create_memberaudit_character(1001)
        cls.skill_type_1 = EveType.objects.get(id=24311)
        cls.skill_type_2 = EveType.objects.get(id=24312)

    def test_has_all_skills(self):
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_1,
            active_skill_level=5,
            skillpoints_in_skill=10,
            trained_skill_level=5,
        )
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_2,
            active_skill_level=5,
            skillpoints_in_skill=10,
            trained_skill_level=5,
        )
        skill_set = SkillSet.objects.create(name="Ship 1")
        SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_1, required_level=5
        )
        SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_2, required_level=3
        )
        skill_set_group = SkillSetGroup.objects.create(name="Dummy")
        skill_set_group.skill_sets.add(skill_set)

        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual(first.failed_required_skills.count(), 0)

    def test_one_skill_below(self):
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_1,
            active_skill_level=5,
            skillpoints_in_skill=10,
            trained_skill_level=5,
        )
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_2,
            active_skill_level=2,
            skillpoints_in_skill=10,
            trained_skill_level=5,
        )
        skill_set = SkillSet.objects.create(name="Ship 1")
        SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_1, required_level=5
        )
        skill_2 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_2, required_level=3
        )
        skill_set_group = SkillSetGroup.objects.create(name="Dummy")
        skill_set_group.skill_sets.add(skill_set)

        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual(
            {obj.pk for obj in first.failed_required_skills.all()}, {skill_2.pk}
        )

    def test_misses_one_skill(self):
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_1,
            active_skill_level=5,
            skillpoints_in_skill=10,
            trained_skill_level=5,
        )
        skill_set = SkillSet.objects.create(name="Ship 1")
        SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_1, required_level=5
        )
        skill_2 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_2, required_level=3
        )
        skill_set_group = SkillSetGroup.objects.create(name="Dummy")
        skill_set_group.skill_sets.add(skill_set)

        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual(
            {obj.pk for obj in first.failed_required_skills.all()}, {skill_2.pk}
        )

    def test_passed_required_and_misses_recommendend_skill(self):
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_1,
            active_skill_level=4,
            skillpoints_in_skill=10,
            trained_skill_level=4,
        )
        skill_set = SkillSet.objects.create(name="Ship 1")
        skill_1 = SkillSetSkill.objects.create(
            skill_set=skill_set,
            eve_type=self.skill_type_1,
            required_level=3,
            recommended_level=5,
        )
        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual({obj.pk for obj in first.failed_required_skills.all()}, set())
        self.assertEqual(
            {obj.pk for obj in first.failed_recommended_skills.all()}, {skill_1.pk}
        )

    def test_misses_recommendend_skill_only(self):
        CharacterSkill.objects.create(
            character=self.character,
            eve_type=self.skill_type_1,
            active_skill_level=4,
            skillpoints_in_skill=10,
            trained_skill_level=4,
        )
        skill_set = SkillSet.objects.create(name="Ship 1")
        skill_1 = SkillSetSkill.objects.create(
            skill_set=skill_set,
            eve_type=self.skill_type_1,
            recommended_level=5,
        )
        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual({obj.pk for obj in first.failed_required_skills.all()}, set())
        self.assertEqual(
            {obj.pk for obj in first.failed_recommended_skills.all()}, {skill_1.pk}
        )

    def test_misses_all_skills(self):
        skill_set = SkillSet.objects.create(name="Ship 1")
        skill_1 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_1, required_level=5
        )
        skill_2 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_2, required_level=3
        )
        skill_set_group = SkillSetGroup.objects.create(name="Dummy")
        skill_set_group.skill_sets.add(skill_set)

        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual(
            {obj.pk for obj in first.failed_required_skills.all()},
            {skill_1.pk, skill_2.pk},
        )

    def test_does_not_require_doctrine_definition(self):
        skill_set = SkillSet.objects.create(name="Ship 1")
        skill_1 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_1, required_level=5
        )
        skill_2 = SkillSetSkill.objects.create(
            skill_set=skill_set, eve_type=self.skill_type_2, required_level=3
        )

        self.character.update_skill_sets()

        self.assertEqual(self.character.skill_set_checks.count(), 1)
        first = self.character.skill_set_checks.first()
        self.assertEqual(first.skill_set.pk, skill_set.pk)
        self.assertEqual(
            {obj.pk for obj in first.failed_required_skills.all()},
            {skill_1.pk, skill_2.pk},
        )


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateSkillQueue(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create(self, mock_esi):
        """can create skill queue from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_skill_queue()
        self.assertEqual(self.character_1001.skillqueue.count(), 3)

        entry = self.character_1001.skillqueue.get(queue_position=0)
        self.assertEqual(entry.eve_type, EveType.objects.get(id=24311))
        self.assertEqual(entry.finish_date, parse_datetime("2016-06-29T10:47:00Z"))
        self.assertEqual(entry.finished_level, 3)
        self.assertEqual(entry.start_date, parse_datetime("2016-06-29T10:46:00Z"))

        entry = self.character_1001.skillqueue.get(queue_position=1)
        self.assertEqual(entry.eve_type, EveType.objects.get(id=24312))
        self.assertEqual(entry.finish_date, parse_datetime("2016-07-15T10:47:00Z"))
        self.assertEqual(entry.finished_level, 4)
        self.assertEqual(entry.level_end_sp, 1000)
        self.assertEqual(entry.level_start_sp, 100)
        self.assertEqual(entry.start_date, parse_datetime("2016-06-29T10:47:00Z"))
        self.assertEqual(entry.training_start_sp, 50)

        entry = self.character_1001.skillqueue.get(queue_position=2)
        self.assertEqual(entry.eve_type, EveType.objects.get(id=24312))
        self.assertEqual(entry.finished_level, 5)

    def test_update_1(self, mock_esi):
        """can update existing skill queue"""
        mock_esi.client = esi_client_stub
        self.character_1001.skillqueue.create(
            queue_position=0,
            eve_type=EveType.objects.get(id=24311),
            finish_date=now() + dt.timedelta(days=1),
            finished_level=4,
            start_date=now() - dt.timedelta(days=1),
        )

        self.character_1001.update_skill_queue()
        self.assertEqual(self.character_1001.skillqueue.count(), 3)

        entry = self.character_1001.skillqueue.get(queue_position=0)
        self.assertEqual(entry.eve_type, EveType.objects.get(id=24311))
        self.assertEqual(entry.finish_date, parse_datetime("2016-06-29T10:47:00Z"))
        self.assertEqual(entry.finished_level, 3)
        self.assertEqual(entry.start_date, parse_datetime("2016-06-29T10:46:00Z"))

    def test_skip_update_1(self, mock_esi):
        """when ESI data has not changed, then skip update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_skill_queue()
        entry = self.character_1001.skillqueue.get(queue_position=0)
        entry.finished_level = 4
        entry.save()

        self.character_1001.update_skill_queue()
        entry = self.character_1001.skillqueue.get(queue_position=0)
        self.assertEqual(entry.finished_level, 4)

    def test_skip_update_2(self, mock_esi):
        """when ESI data has not changed and update is forced, then do update"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_skill_queue()
        entry = self.character_1001.skillqueue.get(queue_position=0)
        entry.finished_level = 4
        entry.save()

        self.character_1001.update_skill_queue(force_update=True)
        entry = self.character_1001.skillqueue.get(queue_position=0)
        self.assertEqual(entry.finished_level, 3)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateWalletJournal(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_update_wallet_balance(self, mock_esi):
        mock_esi.client = esi_client_stub

        self.character_1001.update_wallet_balance()
        self.assertEqual(self.character_1001.wallet_balance.total, 123456789)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_wallet_journal_1(self, mock_esi):
        """can create wallet journal entry from scratch"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_wallet_journal()

        self.assertSetEqual(
            set(self.character_1001.wallet_journal.values_list("entry_id", flat=True)),
            {89, 91},
        )
        obj = self.character_1001.wallet_journal.get(entry_id=89)
        self.assertEqual(obj.amount, -100_000)
        self.assertEqual(float(obj.balance), 500_000.43)
        self.assertEqual(obj.context_id, 4)
        self.assertEqual(obj.context_id_type, obj.CONTEXT_ID_TYPE_CONTRACT_ID)
        self.assertEqual(obj.date, parse_datetime("2018-02-23T14:31:32Z"))
        self.assertEqual(obj.description, "Contract Deposit")
        self.assertEqual(obj.first_party.id, 2001)
        self.assertEqual(obj.reason, "just for fun")
        self.assertEqual(obj.ref_type, "contract_deposit")
        self.assertEqual(obj.second_party.id, 2002)

        obj = self.character_1001.wallet_journal.get(entry_id=91)
        self.assertEqual(
            obj.ref_type, "agent_mission_time_bonus_reward_corporation_tax"
        )

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_wallet_journal_2(self, mock_esi):
        """can add entry to existing wallet journal"""
        mock_esi.client = esi_client_stub
        CharacterWalletJournalEntry.objects.create(
            character=self.character_1001,
            entry_id=1,
            amount=1_000_000,
            balance=10_000_000,
            context_id_type=CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
            date=now(),
            description="dummy",
            first_party=EveEntity.objects.get(id=1001),
            second_party=EveEntity.objects.get(id=1002),
        )

        self.character_1001.update_wallet_journal()

        self.assertSetEqual(
            set(self.character_1001.wallet_journal.values_list("entry_id", flat=True)),
            {1, 89, 91},
        )

        obj = self.character_1001.wallet_journal.get(entry_id=89)
        self.assertEqual(obj.amount, -100_000)
        self.assertEqual(float(obj.balance), 500_000.43)
        self.assertEqual(obj.context_id, 4)
        self.assertEqual(obj.context_id_type, obj.CONTEXT_ID_TYPE_CONTRACT_ID)
        self.assertEqual(obj.date, parse_datetime("2018-02-23T14:31:32Z"))
        self.assertEqual(obj.description, "Contract Deposit")
        self.assertEqual(obj.first_party.id, 2001)
        self.assertEqual(obj.ref_type, "contract_deposit")
        self.assertEqual(obj.second_party.id, 2002)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_update_wallet_journal_3(self, mock_esi):
        """does not update existing entries"""
        mock_esi.client = esi_client_stub
        CharacterWalletJournalEntry.objects.create(
            character=self.character_1001,
            entry_id=89,
            amount=1_000_000,
            balance=10_000_000,
            context_id_type=CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
            date=now(),
            description="dummy",
            first_party=EveEntity.objects.get(id=1001),
            second_party=EveEntity.objects.get(id=1002),
        )

        self.character_1001.update_wallet_journal()

        self.assertSetEqual(
            set(self.character_1001.wallet_journal.values_list("entry_id", flat=True)),
            {89, 91},
        )
        obj = self.character_1001.wallet_journal.get(entry_id=89)
        self.assertEqual(obj.amount, 1_000_000)
        self.assertEqual(float(obj.balance), 10_000_000)
        self.assertEqual(
            obj.context_id_type, CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED
        )
        self.assertEqual(obj.description, "dummy")
        self.assertEqual(obj.first_party.id, 1001)
        self.assertEqual(obj.second_party.id, 1002)

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 10)
    def test_update_wallet_journal_4(self, mock_esi):
        """When new wallet entry is older than retention limit, then do not store it"""
        mock_esi.client = esi_client_stub

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2018, 3, 11, 20, 5), UTC)
            self.character_1001.update_wallet_journal()

        self.assertSetEqual(
            set(self.character_1001.wallet_journal.values_list("entry_id", flat=True)),
            {91},
        )

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 20)
    def test_update_wallet_journal_5(self, mock_esi):
        """When wallet existing entry is older than retention limit, then delete it"""
        mock_esi.client = esi_client_stub
        CharacterWalletJournalEntry.objects.create(
            character=self.character_1001,
            entry_id=55,
            amount=1_000_000,
            balance=10_000_000,
            context_id_type=CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
            date=make_aware(dt.datetime(2018, 2, 11, 20, 5), UTC),
            description="dummy",
            first_party=EveEntity.objects.get(id=1001),
            second_party=EveEntity.objects.get(id=1002),
        )

        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = make_aware(dt.datetime(2018, 3, 11, 20, 5), UTC)
            self.character_1001.update_wallet_journal()

        self.assertSetEqual(
            set(self.character_1001.wallet_journal.values_list("entry_id", flat=True)),
            {89, 91},
        )


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateWalletTransaction(TestCharacterUpdateBase):
    def test_should_add_wallet_transactions_from_scratch(self, mock_esi):
        # given
        mock_esi.client = esi_client_stub
        # when
        with patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None):
            self.character_1001.update_wallet_transactions()
        # then
        self.assertSetEqual(
            set(
                self.character_1001.wallet_transactions.values_list(
                    "transaction_id", flat=True
                )
            ),
            {42},
        )
        obj = self.character_1001.wallet_transactions.get(transaction_id=42)
        self.assertEqual(obj.client, EveEntity.objects.get(id=1003))
        self.assertEqual(obj.date, parse_datetime("2016-10-24T09:00:00Z"))
        self.assertTrue(obj.is_buy)
        self.assertTrue(obj.is_personal)
        self.assertIsNone(obj.journal_ref)
        self.assertEqual(obj.location, Location.objects.get(id=60003760))
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.eve_type, EveType.objects.get(id=603))
        self.assertEqual(float(obj.unit_price), 450000.99)

    def test_should_add_wallet_transactions_from_scratch_with_journal_ref(
        self, mock_esi
    ):
        # given
        mock_esi.client = esi_client_stub
        journal_entry = CharacterWalletJournalEntry.objects.create(
            character=self.character_1001,
            entry_id=67890,
            amount=450000.99,
            balance=10_000_000,
            context_id_type=CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
            date=parse_datetime("2016-10-24T09:00:00Z"),
            description="dummy",
            first_party=EveEntity.objects.get(id=1001),
            second_party=EveEntity.objects.get(id=1003),
        )
        # when
        with patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None):
            self.character_1001.update_wallet_transactions()
        # then
        self.assertSetEqual(
            set(
                self.character_1001.wallet_transactions.values_list(
                    "transaction_id", flat=True
                )
            ),
            {42},
        )
        obj = self.character_1001.wallet_transactions.get(transaction_id=42)
        self.assertEqual(obj.journal_ref, journal_entry)


class TestDataRetentionCutoff(TestCase):
    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", 10)
    def test_limit_is_set(self):
        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = dt.datetime(2020, 12, 19, 16, 15)
            self.assertEqual(data_retention_cutoff(), dt.datetime(2020, 12, 9, 16, 0))

    @patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
    def test_limit_not_set(self):
        with patch(MODELS_PATH + ".character.now") as mock_now:
            mock_now.return_value = dt.datetime(2020, 12, 19, 16, 15)
            self.assertIsNone(data_retention_cutoff())


class TestLocation(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()

    def test_str(self):
        location = Location.objects.get(id=1000000000001)
        self.assertEqual(str(location), "Amamake - Test Structure Alpha")

    def test_repr(self):
        location = Location.objects.get(id=1000000000001)
        self.assertEqual(
            repr(location),
            "Location(id=1000000000001, name='Amamake - Test Structure Alpha')",
        )

    def test_is_solar_system(self):
        location = Location.objects.create(
            id=30000142, eve_solar_system=EveSolarSystem.objects.get(id=30000142)
        )
        self.assertTrue(location.is_solar_system)
        self.assertFalse(location.is_station)
        self.assertFalse(location.is_structure)

    def test_is_station(self):
        location = Location.objects.get(id=60003760)
        self.assertFalse(location.is_solar_system)
        self.assertTrue(location.is_station)
        self.assertFalse(location.is_structure)

    def test_is_structure(self):
        location = Location.objects.get(id=1000000000001)
        self.assertFalse(location.is_solar_system)
        self.assertFalse(location.is_station)
        self.assertTrue(location.is_structure)

    def test_solar_system_url(self):
        obj_1 = Location.objects.get(id=1000000000001)
        obj_2 = Location.objects.create(id=1000000000999)

        self.assertIn("Amamake", obj_1.solar_system_url)
        self.assertEqual("", obj_2.solar_system_url)


class TestCharacterWalletJournalEntry(NoSocketsTestCase):
    def test_match_context_type_id(self):
        self.assertEqual(
            CharacterWalletJournalEntry.match_context_type_id("character_id"),
            CharacterWalletJournalEntry.CONTEXT_ID_TYPE_CHARACTER_ID,
        )
        self.assertEqual(
            CharacterWalletJournalEntry.match_context_type_id("contract_id"),
            CharacterWalletJournalEntry.CONTEXT_ID_TYPE_CONTRACT_ID,
        )
        self.assertEqual(
            CharacterWalletJournalEntry.match_context_type_id(None),
            CharacterWalletJournalEntry.CONTEXT_ID_TYPE_UNDEFINED,
        )


# class TestCharacterMailingList(TestCharacterUpdateBase):
#     def test_name_plus_1(self):
#         """when mailing list has name then return it's name"""
#         mailing_list = CharacterMailingList(
#             self.character_1001, list_id=99, name="Avengers Talk"
#         )
#         self.assertEqual(mailing_list.name_plus, "Avengers Talk")

#     def test_name_plus_2(self):
#         """when mailing list has no name then return a generic name"""
#         mailing_list = CharacterMailingList(self.character_1001, list_id=99)
#         self.assertEqual(mailing_list.name_plus, "Mailing list #99")


class TestCharacter(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)
        self.user = self.character_1001.character_ownership.user

    def test_is_main_1(self):
        self.assertTrue(self.character_1001.is_main)

    def test_is_main_2(self):
        character_1101 = add_memberaudit_character_to_user(self.user, 1101)
        self.assertTrue(self.character_1001.is_main)
        self.assertFalse(character_1101.is_main)

    def test_is_main_3(self):
        self.user.profile.main_character = None
        self.user.profile.save()
        self.assertFalse(self.character_1001.is_main)


class TestMailEntity(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def test_str(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(1001)
        self.assertEqual(str(obj), "Bruce Wayne")

    def test_repr(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(1001)
        self.assertEqual(
            repr(obj), "MailEntity(id=1001, category=CH, name='Bruce Wayne')"
        )

    def test_eve_entity_categories(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(1001)
        self.assertSetEqual(
            obj.eve_entity_categories,
            {
                MailEntity.Category.ALLIANCE,
                MailEntity.Category.CHARACTER,
                MailEntity.Category.CORPORATION,
            },
        )

    def test_name_plus_1(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(1001)
        self.assertEqual(obj.name_plus, "Bruce Wayne")

    def test_name_plus_2(self):
        obj = MailEntity.objects.create(id=42, category=MailEntity.Category.ALLIANCE)
        self.assertEqual(obj.name_plus, "Alliance #42")

    def test_need_to_specify_category(self):
        with self.assertRaises(ValidationError):
            MailEntity.objects.create(id=1)

    def test_url_1(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(3001)
        self.assertIn("dotlan", obj.external_url())

    def test_url_2(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(2001)
        self.assertIn("dotlan", obj.external_url())

    def test_url_3(self):
        obj, _ = MailEntity.objects.update_or_create_from_eve_entity_id(1001)
        self.assertIn("evewho", obj.external_url())

    def test_url_4(self):
        obj = MailEntity.objects.create(
            id=42, category=MailEntity.Category.MAILING_LIST, name="Dummy"
        )
        self.assertEqual(obj.external_url(), "")

    def test_url_5(self):
        obj = MailEntity.objects.create(id=9887, category=MailEntity.Category.ALLIANCE)
        self.assertEqual(obj.external_url(), "")

    def test_url_6(self):
        obj = MailEntity.objects.create(
            id=9887, category=MailEntity.Category.CORPORATION
        )
        self.assertEqual(obj.external_url(), "")


@patch(MODELS_PATH + ".character.esi")
class TestCharacterUpdateAttributes(TestCharacterUpdateBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create(self, mock_esi):
        """can load attributes from test data"""
        mock_esi.client = esi_client_stub

        self.character_1001.update_attributes()
        self.assertEqual(
            self.character_1001.attributes.accrued_remap_cooldown_date,
            parse_datetime("2016-10-24T09:00:00Z"),
        )

        self.assertEqual(
            self.character_1001.attributes.last_remap_date,
            parse_datetime("2016-10-24T09:00:00Z"),
        )

        self.assertEqual(self.character_1001.attributes.charisma, 16)
        self.assertEqual(self.character_1001.attributes.intelligence, 17)
        self.assertEqual(self.character_1001.attributes.memory, 18)
        self.assertEqual(self.character_1001.attributes.perception, 19)
        self.assertEqual(self.character_1001.attributes.willpower, 20)

    def test_update(self, mock_esi):
        """can create attributes from scratch"""
        mock_esi.client = esi_client_stub

        CharacterAttributes.objects.create(
            character=self.character_1001,
            accrued_remap_cooldown_date="2020-10-24T09:00:00Z",
            last_remap_date="2020-10-24T09:00:00Z",
            bonus_remaps=4,
            charisma=102,
            intelligence=103,
            memory=104,
            perception=105,
            willpower=106,
        )

        self.character_1001.update_attributes()
        self.character_1001.attributes.refresh_from_db()

        self.assertEqual(
            self.character_1001.attributes.accrued_remap_cooldown_date,
            parse_datetime("2016-10-24T09:00:00Z"),
        )

        self.assertEqual(
            self.character_1001.attributes.last_remap_date,
            parse_datetime("2016-10-24T09:00:00Z"),
        )

        self.assertEqual(self.character_1001.attributes.charisma, 16)
        self.assertEqual(self.character_1001.attributes.intelligence, 17)
        self.assertEqual(self.character_1001.attributes.memory, 18)
        self.assertEqual(self.character_1001.attributes.perception, 19)
        self.assertEqual(self.character_1001.attributes.willpower, 20)


class TestCharacterShip(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.user = cls.character_1001.character_ownership.user

    def test_str(self):
        # given
        CharacterShip.objects.create(
            character=self.character_1001, eve_type=EveType.objects.get(id=603)
        )
        # when
        result = str(self.character_1001.ship)
        # then
        self.assertIn("Bruce Wayne", result)
        self.assertIn("Merlin", result)


class TestGeneralUserHasAccess(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.character_1002 = create_memberaudit_character(1002)
        cls.user_1002 = cls.character_1002.character_ownership.user
        cls.character_1003 = create_memberaudit_character(1003)
        cls.user_1003 = cls.character_1003.character_ownership.user
        cls.character_1101 = create_memberaudit_character(1101)
        cls.user_1101 = cls.character_1101.character_ownership.user
        cls.user_dummy = AuthUtils.create_user("No-access-to-Member-Audit")

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)
        self.user_1001 = self.character_1001.character_ownership.user

    def test_should_see_own_user_only(self):
        # when
        result = General.accessible_users(user=self.user_1001)
        # then
        self.assertSetEqual(queryset_pks(result), {self.user_1001.pk})

    def test_should_see_all_memberaudit_users(self):
        # given
        self.user_1001 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_everything", self.user_1001
        )
        # when
        result = General.accessible_users(user=self.user_1001)
        # then
        self.assertSetEqual(
            queryset_pks(result),
            {
                self.user_1001.pk,
                self.user_1002.pk,
                self.user_1003.pk,
                self.user_1101.pk,
            },
        )

    def test_should_see_own_alliance_only(self):
        # given
        self.user_1001 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", self.user_1001
        )
        # when
        result = General.accessible_users(user=self.user_1001)
        # then
        self.assertSetEqual(
            queryset_pks(result),
            {self.user_1001.pk, self.user_1002.pk, self.user_1003.pk},
        )

    def test_should_see_own_corporation_only(self):
        # given
        self.user_1001 = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", self.user_1001
        )
        # when
        result = General.accessible_users(user=self.user_1001)
        # then
        self.assertSetEqual(
            queryset_pks(result),
            {self.user_1001.pk, self.user_1002.pk},
        )
