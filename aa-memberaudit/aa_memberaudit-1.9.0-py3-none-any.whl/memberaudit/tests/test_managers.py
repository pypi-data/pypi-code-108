import datetime as dt
from unittest.mock import Mock, patch

from bravado.exception import HTTPForbidden, HTTPNotFound, HTTPUnauthorized

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils.timezone import now
from eveuniverse.models import EveEntity, EveMarketPrice, EveSolarSystem, EveType

from allianceauth.eveonline.models import EveAllianceInfo
from allianceauth.tests.auth_utils import AuthUtils
from app_utils.esi import EsiStatus
from app_utils.testing import NoSocketsTestCase

from ..models import (
    Character,
    CharacterAsset,
    CharacterMailLabel,
    CharacterUpdateStatus,
    Location,
    MailEntity,
)
from . import add_memberaudit_character_to_user, create_memberaudit_character
from .testdata.esi_client_stub import esi_client_stub
from .testdata.esi_test_tools import BravadoResponseStub
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse
from .testdata.load_locations import load_locations

MODELS_PATH = "memberaudit.models"
MANAGERS_PATH = "memberaudit.managers"


class TestCharacterAssetManager(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character = create_memberaudit_character(1001)
        cls.jita_44 = Location.objects.get(id=60003760)
        cls.merlin = EveType.objects.get(id=603)

    def test_can_calculate_pricing(self):
        CharacterAsset.objects.create(
            character=self.character,
            item_id=1100000000666,
            location=self.jita_44,
            eve_type=self.merlin,
            is_singleton=False,
            quantity=5,
        )
        EveMarketPrice.objects.create(eve_type=self.merlin, average_price=500000)
        asset = CharacterAsset.objects.annotate_pricing().first()
        self.assertEqual(asset.price, 500000)
        self.assertEqual(asset.total, 2500000)

    def test_does_not_price_blueprint_copies(self):
        CharacterAsset.objects.create(
            character=self.character,
            item_id=1100000000666,
            location=self.jita_44,
            eve_type=self.merlin,
            is_blueprint_copy=True,
            is_singleton=False,
            quantity=1,
        )
        EveMarketPrice.objects.create(eve_type=self.merlin, average_price=500000)
        asset = CharacterAsset.objects.annotate_pricing().first()
        self.assertIsNone(asset.price)
        self.assertIsNone(asset.total)


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


class TestCharacterMailLabelManager(TestCharacterUpdateBase):
    def test_normal(self):
        label_1 = CharacterMailLabel.objects.create(
            character=self.character_1001, label_id=1, name="Alpha"
        )
        label_2 = CharacterMailLabel.objects.create(
            character=self.character_1001, label_id=2, name="Bravo"
        )
        labels = CharacterMailLabel.objects.get_all_labels()
        self.assertDictEqual(
            labels, {label_1.label_id: label_1, label_2.label_id: label_2}
        )

    def test_empty(self):
        labels = CharacterMailLabel.objects.get_all_labels()
        self.assertDictEqual(labels, dict())


class TestCharacterManager(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.character_1002 = create_memberaudit_character(1002)

    def test_should_return_set_of_eve_character_ids(self):
        self.assertSetEqual(Character.objects.all().eve_character_ids(), {1001, 1002})


class TestCharacterManagerUserHasAccess(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        # main character with alts
        cls.character_1001 = create_memberaudit_character(1001)  # main
        cls.character_1110 = add_memberaudit_character_to_user(  # alt
            cls.character_1001.character_ownership.user, 1110
        )
        cls.character_1121 = add_memberaudit_character_to_user(  # alt
            cls.character_1001.character_ownership.user, 1121
        )
        # main character with alts
        cls.character_1002 = create_memberaudit_character(1002)
        cls.character_1002.is_shared = True
        cls.character_1002.save()
        AuthUtils.add_permission_to_user_by_name(
            "memberaudit.share_characters",
            cls.character_1002.character_ownership.user,
        )
        cls.character_1103 = add_memberaudit_character_to_user(
            cls.character_1002.character_ownership.user, 1103
        )
        # main characters
        cls.character_1003 = create_memberaudit_character(1003)
        cls.character_1101 = create_memberaudit_character(1101)
        cls.character_1102 = create_memberaudit_character(1102)
        cls.character_1102.is_shared = True
        cls.character_1102.save()
        AuthUtils.add_permission_to_user_by_name(
            "memberaudit.share_characters",
            cls.character_1102.character_ownership.user,
        )
        cls.character_1111 = create_memberaudit_character(1111)
        cls.character_1122 = create_memberaudit_character(1122)
        cls.member_state = AuthUtils.get_member_state()
        cls.member_state.member_alliances.add(
            EveAllianceInfo.objects.get(alliance_id=3001)
        )

    def test_user_owning_character_has_access(self):
        """
        when user is the owner of characters
        then include those characters only
        """
        result_qs = Character.objects.user_has_access(
            user=self.character_1001.character_ownership.user
        )
        self.assertSetEqual(result_qs.eve_character_ids(), {1001, 1110, 1121})

    def test_view_own_corporation_1(self):
        """
        when user has permission to view own corporation and not characters_access
        then include own characters only
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(result_qs.eve_character_ids(), {1001, 1110, 1121})

    def test_view_own_corporation_2(self):
        """
        when user has permission to view own corporation and characters_access
        then include characters of corporations members (mains + alts)
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_corporation", user
        )
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(
            result_qs.eve_character_ids(), {1001, 1110, 1121, 1002, 1103}
        )

    def test_view_own_alliance_1a(self):
        """
        when user has permission to view own alliance and not characters_access
        then include own character only
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(result_qs.eve_character_ids(), {1001, 1110, 1121})

    def test_view_own_alliance_1b(self):
        """
        when user has permission to view own alliance and characters_access
        then include characters of alliance members (mains + alts)
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user
        )
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(
            result_qs.eve_character_ids(), {1001, 1110, 1121, 1002, 1003, 1103}
        )

    def test_view_own_alliance_2(self):
        """
        when user has permission to view own alliance and characters_access
        and does not belong to any alliance
        then do not include any alliance characters
        """
        user = self.character_1102.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_same_alliance", user
        )
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(result_qs.eve_character_ids(), {1102})

    def test_view_everything_1(self):
        """
        when user has permission to view everything and no characters_access
        then include own character only
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_everything", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(result_qs.eve_character_ids(), {1001, 1110, 1121})

    def test_view_everything_2(self):
        """
        when user has permission to view everything and characters_access
        then include all characters
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_everything", user
        )
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.characters_access", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(
            result_qs.eve_character_ids(),
            {1001, 1002, 1003, 1101, 1102, 1103, 1110, 1111, 1121, 1122},
        )

    def test_recruiter_access(self):
        """
        when user has recruiter permission
        then include own character plus shared characters from members
        """
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_shared_characters", user
        )
        result_qs = Character.objects.user_has_access(user=user)
        self.assertSetEqual(
            result_qs.eve_character_ids(), {1001, 1002, 1102, 1110, 1121}
        )

    def test_recruiter_should_loose_access_once_recruit_becomes_member(self):
        # given
        character_1107 = create_memberaudit_character(1107)
        character_1107.is_shared = True
        character_1107.save()
        user = self.character_1001.character_ownership.user
        user = AuthUtils.add_permission_to_user_by_name(
            "memberaudit.view_shared_characters", user
        )
        # when
        result_qs = Character.objects.user_has_access(user=user)
        self.assertNotIn(1107, result_qs.eve_character_ids())


class TestMailEntityManager(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def test_get_or_create_esi_1(self):
        """When entity already exists, return it"""
        MailEntity.objects.create(
            id=1234, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        obj, created = MailEntity.objects.get_or_create_esi(id=1234)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "John Doe")

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_get_or_create_esi_2(self, mock_fetch_esi_status):
        """When entity does not exist, create it from ESI / existing EveEntity"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.get_or_create_esi(id=1001)

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_update_or_create_esi_1(self, mock_fetch_esi_status):
        """When entity does not exist, create it from ESI / existing EveEntity"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.update_or_create_esi(id=1001)

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_update_or_create_esi_2(self):
        """When entity already exist and is not a mailing list,
        then update it from ESI / existing EveEntity
        """
        MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )
        obj, created = MailEntity.objects.update_or_create_esi(id=1001)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_update_or_create_esi_3(self):
        """When entity already exist and is a mailing list, then do nothing"""
        MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Dummy"
        )
        obj, created = MailEntity.objects.update_or_create_esi(id=9001)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.MAILING_LIST)
        self.assertEqual(obj.name, "Dummy")
        # method must not create an EveEntity object for the mailing list
        self.assertFalse(EveEntity.objects.filter(id=9001).exists())

    def test_update_or_create_from_eve_entity_1(self):
        """When entity does not exist, create it from given EveEntity"""
        eve_entity = EveEntity.objects.get(id=1001)
        obj, created = MailEntity.objects.update_or_create_from_eve_entity(eve_entity)

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_update_or_create_from_eve_entity_2(self):
        """When entity already exist, update it from given EveEntity"""
        MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        eve_entity = EveEntity.objects.get(id=1001)
        obj, created = MailEntity.objects.update_or_create_from_eve_entity(eve_entity)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_update_or_create_from_eve_entity_id_1(self):
        """When entity does not exist, create it from given EveEntity"""
        eve_entity = EveEntity.objects.get(id=1001)
        obj, created = MailEntity.objects.update_or_create_from_eve_entity_id(
            eve_entity.id
        )

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_update_or_create_from_eve_entity_id_2(self):
        """When entity already exist, update it from given EveEntity"""
        MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        eve_entity = EveEntity.objects.get(id=1001)
        obj, created = MailEntity.objects.update_or_create_from_eve_entity_id(
            eve_entity.id
        )

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

    def test_bulk_resolve_1(self):
        """Can resolve all 3 categories known by EveEntity"""
        obj_1001 = MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER
        )
        obj_2001 = MailEntity.objects.create(
            id=2001, category=MailEntity.Category.CORPORATION
        )
        obj_3001 = MailEntity.objects.create(
            id=3001, category=MailEntity.Category.ALLIANCE
        )

        MailEntity.objects.bulk_update_names([obj_1001, obj_2001, obj_3001])

        self.assertEqual(obj_1001.name, "Bruce Wayne")
        self.assertEqual(obj_2001.name, "Wayne Technologies")
        self.assertEqual(obj_3001.name, "Wayne Enterprises")

    def test_bulk_resolve_2(self):
        """Will ignore categories not known to EveEntity"""

        obj_1001 = MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER
        )
        obj_9001 = MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST
        )
        obj_9002 = MailEntity.objects.create(
            id=9002, category=MailEntity.Category.UNKNOWN
        )

        MailEntity.objects.bulk_update_names([obj_1001, obj_9001, obj_9002])

        self.assertEqual(obj_1001.name, "Bruce Wayne")
        self.assertEqual(obj_9001.name, "")
        self.assertEqual(obj_9002.name, "")

    def test_bulk_resolve_3(self):
        """When object list is empty, then no op"""

        try:
            MailEntity.objects.bulk_update_names([])
        except Exception as ex:
            self.fail(f"Unexpected exception: {ex}")

    def test_bulk_resolve_4(self):
        """When object already has a name, then update it"""
        obj_1001 = MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        MailEntity.objects.bulk_update_names([obj_1001])

        self.assertEqual(obj_1001.name, "Bruce Wayne")

    def test_bulk_resolve_5(self):
        """When object already has a name and respective option is chosen
        then ignore it
        """
        obj_1001 = MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        MailEntity.objects.bulk_update_names([obj_1001], keep_names=True)

        self.assertEqual(obj_1001.name, "John Doe")


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MANAGERS_PATH + ".general.fetch_esi_status")
class TestMailEntityManagerAsync(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        MailEntity.objects.all().delete()

    def test_get_or_create_esi_async_1(self, mock_fetch_esi_status):
        """When entity already exists, return it"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        MailEntity.objects.create(
            id=1234, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        obj, created = MailEntity.objects.get_or_create_esi_async(id=1234)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "John Doe")
        self.assertFalse(mock_fetch_esi_status.called)  # was esi error status checked

    def test_get_or_create_esi_async_2(self, mock_fetch_esi_status):
        """When entity does not exist and no category specified,
        then create it asynchronously from ESI / existing EveEntity
        """
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.get_or_create_esi_async(id=1001)

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.UNKNOWN)
        self.assertEqual(obj.name, "")

        obj.refresh_from_db()
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")
        self.assertTrue(mock_fetch_esi_status.called)  # was esi error status checked

    def test_get_or_create_esi_async_3(self, mock_fetch_esi_status):
        """When entity does not exist and category is not mailing list,
        then create it synchronously from ESI / existing EveEntity
        """
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.get_or_create_esi_async(
            id=1001, category=MailEntity.Category.CHARACTER
        )

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")
        self.assertFalse(mock_fetch_esi_status.called)  # was esi error status checked

    def test_update_or_create_esi_async_1(self, mock_fetch_esi_status):
        """When entity does not exist, create empty object and run task to resolve"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.update_or_create_esi_async(1001)

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.UNKNOWN)
        self.assertEqual(obj.name, "")

        obj.refresh_from_db()
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

        self.assertTrue(mock_fetch_esi_status.called)  # was esi error status checked

    def test_update_or_create_esi_async_2(self, mock_fetch_esi_status):
        """When entity exists and not a mailing list, then update synchronously"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        MailEntity.objects.create(
            id=1001, category=MailEntity.Category.CHARACTER, name="John Doe"
        )

        obj, created = MailEntity.objects.update_or_create_esi_async(1001)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

        self.assertFalse(mock_fetch_esi_status.called)  # was esi error status checked

    def test_update_or_create_esi_async_3(self, mock_fetch_esi_status):
        """When entity exists and is a mailing list, then do nothing"""
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        MailEntity.objects.create(
            id=9001, category=MailEntity.Category.MAILING_LIST, name="Dummy"
        )

        obj, created = MailEntity.objects.update_or_create_esi_async(9001)

        self.assertFalse(created)
        self.assertEqual(obj.category, MailEntity.Category.MAILING_LIST)
        self.assertEqual(obj.name, "Dummy")

        self.assertFalse(mock_fetch_esi_status.called)  # was esi error status checked

    def test_update_or_create_esi_async_4(self, mock_fetch_esi_status):
        """When entity does not exist and category is not a mailing list,
        then create empty object from ESI synchronously
        """
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)

        obj, created = MailEntity.objects.update_or_create_esi_async(
            1001, MailEntity.Category.CHARACTER
        )

        self.assertTrue(created)
        self.assertEqual(obj.category, MailEntity.Category.CHARACTER)
        self.assertEqual(obj.name, "Bruce Wayne")

        self.assertFalse(mock_fetch_esi_status.called)  # was esi error status checked


class TestCharacterUpdateStatusManager(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)

    def test_calculate_stats_1(self):
        """Can handle no data"""
        try:
            CharacterUpdateStatus.objects.statistics()
        except Exception as ex:
            self.fail(f"Unexpected exception {ex} occurred")

    def test_calculate_stats_2(self):
        """normal calculation"""
        my_now = now()
        root_task_id = "1"
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.CONTACTS,
            is_success=True,
            started_at=my_now - dt.timedelta(seconds=30),
            finished_at=my_now,
            root_task_id=root_task_id,
        )
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.SKILLS,
            is_success=True,
            started_at=my_now + dt.timedelta(seconds=10),
            finished_at=my_now + dt.timedelta(seconds=30),
            root_task_id=root_task_id,
        )
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.ASSETS,
            is_success=True,
            started_at=my_now,
            finished_at=my_now + dt.timedelta(seconds=90),
            root_task_id=root_task_id,
        )
        stats = CharacterUpdateStatus.objects.statistics()["update_statistics"]

        # round duration is calculated as total duration
        # from start of first to end of last section
        self.assertEqual(stats["ring_2"]["total"]["duration"], 60)
        self.assertEqual(stats["ring_2"]["total"]["root_task_id"], root_task_id)

        # can identify longest section with character
        self.assertEqual(stats["ring_2"]["first"]["section"], "contacts")
        self.assertEqual(stats["ring_2"]["last"]["section"], "skills")
        self.assertEqual(stats["ring_3"]["max"]["section"], "assets")
        self.assertEqual(stats["ring_3"]["max"]["duration"], 90)


@patch(MANAGERS_PATH + ".general.esi")
class TestLocationManager(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.jita = EveSolarSystem.objects.get(id=30000142)
        cls.amamake = EveSolarSystem.objects.get(id=30002537)
        cls.astrahus = EveType.objects.get(id=35832)
        cls.athanor = EveType.objects.get(id=35835)
        cls.jita_trade_hub = EveType.objects.get(id=52678)
        cls.corporation_2001 = EveEntity.objects.get(id=2001)
        cls.corporation_2002 = EveEntity.objects.get(id=2002)
        cls.character = create_memberaudit_character(1001)
        cls.token = cls.character.character_ownership.user.token_set.first()

    # Structures

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_can_create_structure(self, mock_fetch_esi_status, mock_esi):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi(
            id=1000000000001, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 1000000000001)
        self.assertEqual(obj.name, "Amamake - Test Structure Alpha")
        self.assertEqual(obj.eve_solar_system, self.amamake)
        self.assertEqual(obj.eve_type, self.astrahus)
        self.assertEqual(obj.owner, self.corporation_2001)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_can_update_structure(self, mock_fetch_esi_status, mock_esi):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        obj, _ = Location.objects.update_or_create_esi(
            id=1000000000001, token=self.token
        )
        obj.name = "Not my structure"
        obj.eve_solar_system = self.jita
        obj.eve_type = self.jita_trade_hub
        obj.owner = self.corporation_2002
        obj.save()
        obj, created = Location.objects.update_or_create_esi(
            id=1000000000001, token=self.token
        )
        self.assertFalse(created)
        self.assertEqual(obj.id, 1000000000001)
        self.assertEqual(obj.name, "Amamake - Test Structure Alpha")
        self.assertEqual(obj.eve_solar_system, self.amamake)
        self.assertEqual(obj.eve_type, self.astrahus)
        self.assertEqual(obj.owner, self.corporation_2001)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_does_not_update_existing_location_during_grace_period(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        obj_existing = Location.objects.create(
            id=1000000000001,
            name="Existing Structure",
            eve_solar_system=self.jita,
            eve_type=self.jita_trade_hub,
            owner=self.corporation_2002,
        )
        obj, created = Location.objects.get_or_create_esi(
            id=1000000000001, token=self.token
        )
        self.assertFalse(created)
        self.assertEqual(obj, obj_existing)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_always_update_existing_empty_locations_after_grace_period_1(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        Location.objects.create(id=1000000000001)
        obj, _ = Location.objects.get_or_create_esi(id=1000000000001, token=self.token)
        self.assertIsNone(obj.eve_solar_system)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_always_update_existing_empty_locations_after_grace_period_2(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        mocked_update_at = now() - dt.timedelta(minutes=6)
        with patch("django.utils.timezone.now", Mock(return_value=mocked_update_at)):
            Location.objects.create(id=1000000000001)
            obj, _ = Location.objects.get_or_create_esi(
                id=1000000000001, token=self.token
            )
        self.assertEqual(obj.eve_solar_system, self.amamake)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    @patch(MANAGERS_PATH + ".general.MEMBERAUDIT_LOCATION_STALE_HOURS", 24)
    def test_always_update_existing_locations_which_are_stale(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        mocked_update_at = now() - dt.timedelta(hours=25)
        with patch("django.utils.timezone.now", Mock(return_value=mocked_update_at)):
            Location.objects.create(
                id=1000000000001,
                name="Existing Structure",
                eve_solar_system=self.jita,
                eve_type=self.jita_trade_hub,
                owner=self.corporation_2002,
            )
        obj, created = Location.objects.get_or_create_esi(
            id=1000000000001, token=self.token
        )
        self.assertFalse(created)
        self.assertEqual(obj.eve_solar_system, self.amamake)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_propagates_http_error_on_structure_create(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        with self.assertRaises(HTTPNotFound):
            Location.objects.update_or_create_esi(id=1000000000099, token=self.token)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_always_creates_empty_location_for_invalid_ids(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi(
            id=80000000, token=self.token
        )
        self.assertTrue(created)
        self.assertTrue(obj.is_empty)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_propagates_exceptions_on_structure_create(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client.Universe.get_universe_structures_structure_id.side_effect = (
            RuntimeError
        )

        with self.assertRaises(RuntimeError):
            Location.objects.update_or_create_esi(id=1000000000099, token=self.token)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_can_create_empty_location_on_access_error_1(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client.Universe.get_universe_structures_structure_id.side_effect = (
            HTTPForbidden(response=BravadoResponseStub(403, "Test exception"))
        )

        obj, created = Location.objects.update_or_create_esi(
            id=1000000000099, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 1000000000099)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_can_create_empty_location_on_access_error_2(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client.Universe.get_universe_structures_structure_id.side_effect = (
            HTTPUnauthorized(response=BravadoResponseStub(401, "Test exception"))
        )

        obj, created = Location.objects.update_or_create_esi(
            id=1000000000099, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 1000000000099)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_does_not_creates_empty_location_on_access_errors_if_requested(
        self, mock_fetch_esi_status, mock_esi
    ):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client.Universe.get_universe_structures_structure_id.side_effect = (
            RuntimeError
        )
        with self.assertRaises(RuntimeError):
            Location.objects.update_or_create_esi(id=1000000000099, token=self.token)

    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_records_esi_error_on_access_error(self, mock_fetch_esi_status, mock_esi):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client.Universe.get_universe_structures_structure_id.side_effect = (
            HTTPForbidden(
                response=BravadoResponseStub(
                    403,
                    "Test exception",
                    headers={
                        "X-Esi-Error-Limit-Remain": "40",
                        "X-Esi-Error-Limit-Reset": "30",
                    },
                )
            )
        )

        obj, created = Location.objects.update_or_create_esi(
            id=1000000000099, token=self.token
        )
        self.assertTrue(created)

    # Stations

    def test_can_create_station(self, mock_esi):
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi(
            id=60003760, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 60003760)
        self.assertEqual(obj.name, "Jita IV - Moon 4 - Caldari Navy Assembly Plant")
        self.assertEqual(obj.eve_solar_system, self.jita)
        self.assertEqual(obj.eve_type, self.jita_trade_hub)
        self.assertEqual(obj.owner, self.corporation_2002)

    def test_can_update_station(self, mock_esi):
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi(
            id=60003760, token=self.token
        )
        obj.name = "Not my station"
        obj.eve_solar_system = self.amamake
        obj.eve_type = self.astrahus
        obj.owner = self.corporation_2001
        obj.save()

        obj, created = Location.objects.update_or_create_esi(
            id=60003760, token=self.token
        )
        self.assertFalse(created)
        self.assertEqual(obj.id, 60003760)
        self.assertEqual(obj.name, "Jita IV - Moon 4 - Caldari Navy Assembly Plant")
        self.assertEqual(obj.eve_solar_system, self.jita)
        self.assertEqual(obj.eve_type, self.jita_trade_hub)
        self.assertEqual(obj.owner, self.corporation_2002)

    def test_propagates_http_error_on_station_create(self, mock_esi):
        mock_esi.client = esi_client_stub

        with self.assertRaises(HTTPNotFound):
            Location.objects.update_or_create_esi(id=63999999, token=self.token)

    # Solar System

    def test_can_create_solar_system(self, mock_esi):
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi(
            id=30002537, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 30002537)
        self.assertEqual(obj.name, "Amamake")
        self.assertEqual(obj.eve_solar_system, self.amamake)
        self.assertEqual(obj.eve_type, EveType.objects.get(id=5))
        self.assertIsNone(obj.owner)


@patch(MANAGERS_PATH + ".general.esi")
class TestLocationManagerAsync(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.jita = EveSolarSystem.objects.get(id=30000142)
        cls.amamake = EveSolarSystem.objects.get(id=30002537)
        cls.astrahus = EveType.objects.get(id=35832)
        cls.athanor = EveType.objects.get(id=35835)
        cls.jita_trade_hub = EveType.objects.get(id=52678)
        cls.corporation_2001 = EveEntity.objects.get(id=2001)
        cls.corporation_2002 = EveEntity.objects.get(id=2002)
        cls.character = create_memberaudit_character(1001)
        cls.token = cls.character.character_ownership.user.token_set.first()

    def setUp(self) -> None:
        cache.clear()

    @override_settings(
        CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True
    )
    @patch(MANAGERS_PATH + ".general.fetch_esi_status")
    def test_can_create_structure_async(self, mock_fetch_esi_status, mock_esi):
        mock_fetch_esi_status.return_value = EsiStatus(True, 99, 60)
        mock_esi.client = esi_client_stub

        obj, created = Location.objects.update_or_create_esi_async(
            id=1000000000001, token=self.token
        )
        self.assertTrue(created)
        self.assertEqual(obj.id, 1000000000001)
        self.assertIsNone(obj.eve_solar_system)
        self.assertIsNone(obj.eve_type)

        obj.refresh_from_db()
        self.assertEqual(obj.name, "Amamake - Test Structure Alpha")
        self.assertEqual(obj.eve_solar_system, self.amamake)
        self.assertEqual(obj.eve_type, self.astrahus)
        self.assertEqual(obj.owner, self.corporation_2001)

        self.assertTrue(mock_fetch_esi_status.called)  # proofs task was called
