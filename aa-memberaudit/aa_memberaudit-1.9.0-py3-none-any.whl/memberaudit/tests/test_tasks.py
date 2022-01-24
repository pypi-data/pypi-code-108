import datetime as dt
from unittest.mock import patch

from bravado.exception import HTTPInternalServerError
from celery.exceptions import Retry as CeleryRetry

from django.test import TestCase, override_settings
from django.utils.timezone import now
from esi.models import Token
from eveuniverse.models import EveSolarSystem, EveType

from app_utils.esi import EsiErrorLimitExceeded, EsiOffline, EsiStatus
from app_utils.testing import generate_invalid_pk

from ..models import Character, CharacterAsset, CharacterUpdateStatus, Location
from ..tasks import (
    _export_data_for_topic,
    delete_character,
    export_data,
    run_regular_updates,
    update_all_characters,
    update_character,
    update_character_assets,
    update_character_contacts,
    update_character_contracts,
    update_character_mails,
    update_character_wallet_journal,
    update_characters_skill_checks,
    update_mail_entity_esi,
    update_market_prices,
    update_structure_esi,
)
from . import create_memberaudit_character
from .testdata.esi_client_stub import esi_client_error_stub, esi_client_stub
from .testdata.esi_test_tools import BravadoResponseStub
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse
from .testdata.load_locations import load_locations

MODELS_PATH = "memberaudit.models"
MANAGERS_PATH = "memberaudit.managers"
TASKS_PATH = "memberaudit.tasks"


@patch(TASKS_PATH + ".update_all_characters")
@patch(TASKS_PATH + ".update_market_prices")
class TestRegularUpdates(TestCase):
    @patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
    def test_should_run_update_normally(
        self,
        mock_update_market_prices,
        mock_update_all_characters,
    ):
        run_regular_updates()

        self.assertTrue(mock_update_market_prices.apply_async.called)
        self.assertTrue(mock_update_all_characters.apply_async.called)

    @patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(False, 99, 60))
    def test_should_retry_if_esi_is_down(
        self,
        mock_update_market_prices,
        mock_update_all_characters,
    ):
        with self.assertRaises(CeleryRetry):
            run_regular_updates()

        self.assertFalse(mock_update_market_prices.apply_async.called)
        self.assertFalse(mock_update_all_characters.apply_async.called)

    @patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 1, 60))
    def test_should_retry_if_esi_error_threshold_exceeded(
        self,
        mock_update_market_prices,
        mock_update_all_characters,
    ):
        with self.assertRaises(CeleryRetry):
            run_regular_updates()

        self.assertFalse(mock_update_market_prices.apply_async.called)
        self.assertFalse(mock_update_all_characters.apply_async.called)


@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
class TestOtherTasks(TestCase):
    @patch(TASKS_PATH + ".EveMarketPrice.objects.update_from_esi")
    def test_update_market_prices(self, mock_update_from_esi):
        update_market_prices()
        self.assertTrue(mock_update_from_esi.called)


@override_settings(CELERY_ALWAYS_EAGER=True)  # need to ignore exceptions
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
class TestUpdateCharacterAssets(TestCase):
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

    def test_update_assets_1(self, mock_esi):
        """can create assets from scratch"""
        mock_esi.client = esi_client_stub

        update_character_assets(self.character_1001.pk)
        self.assertSetEqual(
            set(self.character_1001.assets.values_list("item_id", flat=True)),
            {
                1100000000001,
                1100000000002,
                1100000000003,
                1100000000004,
                1100000000005,
                1100000000006,
                1100000000007,
                1100000000008,
            },
        )

        asset = self.character_1001.assets.get(item_id=1100000000001)
        self.assertTrue(asset.is_blueprint_copy)
        self.assertTrue(asset.is_singleton)
        self.assertEqual(asset.location_flag, "Hangar")
        self.assertEqual(asset.location_id, 60003760)
        self.assertEqual(asset.quantity, 1)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=20185))
        self.assertEqual(asset.name, "Parent Item 1")

        asset = self.character_1001.assets.get(item_id=1100000000002)
        self.assertFalse(asset.is_blueprint_copy)
        self.assertTrue(asset.is_singleton)
        self.assertEqual(asset.location_flag, "???")
        self.assertEqual(asset.parent.item_id, 1100000000001)
        self.assertEqual(asset.quantity, 1)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=19540))
        self.assertEqual(asset.name, "Leaf Item 2")

        asset = self.character_1001.assets.get(item_id=1100000000003)
        self.assertEqual(asset.parent.item_id, 1100000000001)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=23))

        asset = self.character_1001.assets.get(item_id=1100000000004)
        self.assertEqual(asset.parent.item_id, 1100000000003)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=19553))

        asset = self.character_1001.assets.get(item_id=1100000000005)
        self.assertEqual(asset.location, self.structure_1)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=20185))

        asset = self.character_1001.assets.get(item_id=1100000000006)
        self.assertEqual(asset.parent.item_id, 1100000000005)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=19540))

        asset = self.character_1001.assets.get(item_id=1100000000007)
        self.assertEqual(asset.location_id, 30000142)
        self.assertEqual(asset.name, "")
        self.assertEqual(asset.eve_type, EveType.objects.get(id=19540))

        asset = self.character_1001.assets.get(item_id=1100000000008)
        self.assertEqual(asset.location_id, 1000000000001)

    def test_update_assets_2(self, mock_esi):
        """can remove obsolete assets"""
        mock_esi.client = esi_client_stub
        CharacterAsset.objects.create(
            character=self.character_1001,
            item_id=1100000000666,
            location=self.jita_44,
            eve_type=EveType.objects.get(id=20185),
            is_singleton=False,
            name="Trucker",
            quantity=1,
        )

        update_character_assets(self.character_1001.pk)
        self.assertSetEqual(
            set(self.character_1001.assets.values_list("item_id", flat=True)),
            {
                1100000000001,
                1100000000002,
                1100000000003,
                1100000000004,
                1100000000005,
                1100000000006,
                1100000000007,
                1100000000008,
            },
        )

    def test_update_assets_3(self, mock_esi):
        """can update existing assets"""
        mock_esi.client = esi_client_stub
        CharacterAsset.objects.create(
            character=self.character_1001,
            item_id=1100000000001,
            location=self.jita_44,
            eve_type=EveType.objects.get(id=20185),
            is_singleton=True,
            name="Parent Item 1",
            quantity=10,
        )

        update_character_assets(self.character_1001.pk)
        self.assertSetEqual(
            set(self.character_1001.assets.values_list("item_id", flat=True)),
            {
                1100000000001,
                1100000000002,
                1100000000003,
                1100000000004,
                1100000000005,
                1100000000006,
                1100000000007,
                1100000000008,
            },
        )

        asset = self.character_1001.assets.get(item_id=1100000000001)
        self.assertTrue(asset.is_singleton)
        self.assertEqual(asset.location_id, 60003760)
        self.assertEqual(asset.quantity, 1)
        self.assertEqual(asset.eve_type, EveType.objects.get(id=20185))
        self.assertEqual(asset.name, "Parent Item 1")

    def test_update_assets_4(self, mock_esi):
        """assets moved to different locations are kept"""
        mock_esi.client = esi_client_stub
        parent_asset = CharacterAsset.objects.create(
            character=self.character_1001,
            item_id=1100000000666,
            location=self.jita_44,
            eve_type=EveType.objects.get(id=20185),
            is_singleton=True,
            name="Obsolete Container",
            quantity=1,
        )
        CharacterAsset.objects.create(
            character=self.character_1001,
            item_id=1100000000002,
            parent=parent_asset,
            eve_type=EveType.objects.get(id=19540),
            is_singleton=True,
            is_blueprint_copy=False,
            quantity=1,
        )

        update_character_assets(self.character_1001.pk)
        self.assertSetEqual(
            set(self.character_1001.assets.values_list("item_id", flat=True)),
            {
                1100000000001,
                1100000000002,
                1100000000003,
                1100000000004,
                1100000000005,
                1100000000006,
                1100000000007,
                1100000000008,
            },
        )

    def test_update_assets_5(self, mock_esi):
        """when update succeeded then report update success"""
        mock_esi.client = esi_client_stub

        update_character_assets(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertTrue(status.is_success)
        self.assertFalse(status.last_error_message)

    def test_update_assets_6(self, mock_esi):
        """when update failed then report the error"""
        mock_esi.client.Assets.get_characters_character_id_assets.side_effect = (
            HTTPInternalServerError(response=BravadoResponseStub(500, "Test exception"))
        )

        with self.assertRaises(OSError):
            update_character_assets(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertFalse(status.is_success)
        self.assertEqual(
            status.last_error_message, "HTTPInternalServerError: 500 Test exception"
        )

    def test_update_assets_7(self, mock_esi):
        """when preload objects failed then report the error"""
        mock_esi.client = esi_client_stub

        with patch(MODELS_PATH + ".character.Location") as m:
            m.objects.get_or_create_esi_async.side_effect = HTTPInternalServerError(
                response=BravadoResponseStub(500, "Test exception")
            )
            with self.assertRaises(OSError):
                update_character_assets(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertFalse(status.is_success)
        self.assertEqual(
            status.last_error_message, "HTTPInternalServerError: 500 Test exception"
        )

    def test_update_assets_8(self, mock_esi):
        """when building the asset tree failed then report the error"""
        mock_esi.client = esi_client_stub

        with patch(MODELS_PATH + ".character.logger") as m:
            m.info.side_effect = HTTPInternalServerError(
                response=BravadoResponseStub(500, "Test exception")
            )
            with self.assertRaises(OSError):
                update_character_assets(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertFalse(status.is_success)
        self.assertEqual(
            status.last_error_message, "HTTPInternalServerError: 500 Test exception"
        )

    def test_update_assets_9(self, mock_esi):
        """when info from ESI has not change, then don't re-create asset tree"""
        mock_esi.client = esi_client_stub

        self.character_1001.reset_update_section(Character.UpdateSection.ASSETS)
        update_character_assets(self.character_1001.pk)
        asset = self.character_1001.assets.get(item_id=1100000000001)
        asset.name = "New Name"
        asset.save()
        update_character_assets(self.character_1001.pk)

        asset = self.character_1001.assets.get(item_id=1100000000001)
        self.assertEqual(asset.name, "New Name")

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertTrue(status.is_success)

    def test_update_assets_10(self, mock_esi):
        """when info from ESI has not change and update is forced, then re-create asset tree"""
        mock_esi.client = esi_client_stub

        self.character_1001.reset_update_section(Character.UpdateSection.ASSETS)
        update_character_assets(self.character_1001.pk)
        asset = self.character_1001.assets.get(item_id=1100000000001)
        asset.name = "New Name"
        asset.save()
        update_character_assets(self.character_1001.pk, force_update=True)

        asset = self.character_1001.assets.get(item_id=1100000000001)
        self.assertEqual(asset.name, "Parent Item 1")

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.ASSETS
        )
        self.assertTrue(status.is_success)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
class TestUpdateCharacterMails(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()

    def test_update_ok(self, mock_esi):
        """when update succeeded then report update success"""
        mock_esi.client = esi_client_stub

        update_character_mails(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.MAILS
        )
        self.assertTrue(status.is_success)
        self.assertFalse(status.last_error_message)

    def test_detect_error(self, mock_esi):
        """when update failed then report the error"""
        mock_esi.client.Mail.get_characters_character_id_mail_lists.side_effect = (
            HTTPInternalServerError(response=BravadoResponseStub(500, "Test exception"))
        )

        try:
            update_character_mails(self.character_1001.pk)
        except Exception:
            status = self.character_1001.update_status_set.get(
                section=Character.UpdateSection.MAILS
            )
            self.assertFalse(status.is_success)
            self.assertEqual(
                status.last_error_message, "HTTPInternalServerError: 500 Test exception"
            )
        else:
            self.assertTrue(False)  # Hack to ensure the test fails when it gets here


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
class TestUpdateCharacterContacts(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()

    def test_update_ok(self, mock_esi):
        """when update succeeded then report update success"""
        mock_esi.client = esi_client_stub

        update_character_contacts(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.CONTACTS
        )
        self.assertTrue(status.is_success)
        self.assertFalse(status.last_error_message)

    def test_detect_error(self, mock_esi):
        """when update failed then report the error"""
        mock_esi.client.Contacts.get_characters_character_id_contacts_labels.side_effect = HTTPInternalServerError(
            response=BravadoResponseStub(500, "Test exception")
        )

        try:
            update_character_contacts(self.character_1001.pk)
        except Exception:
            status = self.character_1001.update_status_set.get(
                section=Character.UpdateSection.CONTACTS
            )
            self.assertFalse(status.is_success)
            self.assertEqual(
                status.last_error_message, "HTTPInternalServerError: 500 Test exception"
            )
        else:
            self.assertTrue(False)  # Hack to ensure the test fails when it gets here


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
class TestUpdateCharacterContracts(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()

    def test_update_ok(self, mock_esi):
        """when update succeeded then report update success"""
        mock_esi.client = esi_client_stub

        update_character_contracts(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.CONTRACTS
        )
        self.assertTrue(status.is_success)
        self.assertFalse(status.last_error_message)

    def test_detect_error(self, mock_esi):
        """when update failed then report the error"""
        mock_esi.client.Contracts.get_characters_character_id_contracts.side_effect = (
            HTTPInternalServerError(response=BravadoResponseStub(500, "Test exception"))
        )

        try:
            update_character_contracts(self.character_1001.pk)
        except Exception:
            status = self.character_1001.update_status_set.get(
                section=Character.UpdateSection.CONTRACTS
            )
            self.assertFalse(status.is_success)
            self.assertEqual(
                status.last_error_message, "HTTPInternalServerError: 500 Test exception"
            )
        else:
            self.assertTrue(False)  # Hack to ensure the test fails when it gets here


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
class TestUpdateCharacterWalletJournal(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        cls.character_1001 = create_memberaudit_character(1001)
        cls.token = cls.character_1001.character_ownership.user.token_set.first()

    def test_update_ok(self, mock_esi):
        """when update succeeded then report update success"""
        mock_esi.client = esi_client_stub

        update_character_wallet_journal(self.character_1001.pk)

        status = self.character_1001.update_status_set.get(
            section=Character.UpdateSection.WALLET_JOURNAL
        )
        self.assertTrue(status.is_success)
        self.assertFalse(status.last_error_message)

    def test_detect_error(self, mock_esi):
        """when update failed then report the error"""
        mock_esi.client.Wallet.get_characters_character_id_wallet_journal.side_effect = HTTPInternalServerError(
            response=BravadoResponseStub(500, "Test exception")
        )

        try:
            update_character_wallet_journal(self.character_1001.pk)
        except Exception:
            status = self.character_1001.update_status_set.get(
                section=Character.UpdateSection.WALLET_JOURNAL
            )
            self.assertFalse(status.is_success)
            self.assertEqual(
                status.last_error_message, "HTTPInternalServerError: 500 Test exception"
            )
        else:
            self.assertTrue(False)  # Hack to ensure the test fails when it gets here


@patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(MODELS_PATH + ".character.esi")
@override_settings(CELERY_ALWAYS_EAGER=True)
class TestUpdateCharacter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)

    def test_should_update_normally(self, mock_esi):
        """can update from scratch"""
        mock_esi.client = esi_client_stub

        result = update_character(self.character_1001.pk)
        self.assertTrue(result)
        self.assertTrue(self.character_1001.is_update_status_ok())

    def test_should_report_errors_during_updates(self, mock_esi):
        mock_esi.client = esi_client_error_stub

        with self.assertRaises(OSError):  # raised when trying to fetch attributes
            update_character(self.character_1001.pk)

        self.assertFalse(self.character_1001.is_update_status_ok())

        status = self.character_1001.update_status_set.get(
            character=self.character_1001,
            section=Character.UpdateSection.ATTRIBUTES,
        )
        self.assertFalse(status.is_success)
        self.assertEqual(
            status.last_error_message, "HTTPInternalServerError: 500 Test exception"
        )
        self.assertTrue(status.finished_at)

    @patch(TASKS_PATH + ".Character.update_loyalty")
    def test_should_update_stale_sections_only_1(self, update_loyalty, mock_esi):
        """normal section"""
        mock_esi.client = esi_client_stub
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.LOYALTY,
            is_success=True,
            started_at=now() - dt.timedelta(seconds=30),
            finished_at=now(),
        )

        update_character(self.character_1001.pk)

        self.assertFalse(update_loyalty.called)

    @patch(TASKS_PATH + ".update_character_mails")
    def test_should_update_stale_sections_only_2(
        self, update_character_mails, mock_esi
    ):
        """special section"""
        mock_esi.client = esi_client_stub
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.MAILS,
            is_success=True,
            started_at=now() - dt.timedelta(seconds=30),
            finished_at=now(),
        )

        update_character(self.character_1001.pk)

        self.assertFalse(update_character_mails.apply_async.called)

    @patch(TASKS_PATH + ".Character.update_skills", spec=True)
    def test_should_update_stale_sections_only_3(self, mock_update_skills, mock_esi):
        """When generic section has recently been updated and force_update is called
        then update again
        """
        mock_esi.client = esi_client_stub
        CharacterUpdateStatus.objects.create(
            character=self.character_1001,
            section=Character.UpdateSection.SKILLS,
            is_success=True,
            started_at=now() - dt.timedelta(seconds=30),
            finished_at=now(),
        )

        update_character(self.character_1001.pk, force_update=True)

        self.assertTrue(mock_update_skills.called)

    def test_no_update_required(self, mock_esi):
        """Do not update anything when not required"""
        mock_esi.client = esi_client_stub
        for section in Character.UpdateSection.values:
            CharacterUpdateStatus.objects.create(
                character=self.character_1001,
                section=section,
                is_success=True,
                started_at=now() - dt.timedelta(seconds=30),
                finished_at=now(),
            )

        result = update_character(self.character_1001.pk)
        self.assertFalse(result)

    def test_update_forced(self, mock_esi):
        """Can do forced update"""
        mock_esi.client = esi_client_stub

        result = update_character(self.character_1001.pk, force_update=True)
        self.assertTrue(result)
        self.assertTrue(self.character_1001.is_update_status_ok())


@patch(
    TASKS_PATH + ".Character.objects.get_cached",
    lambda pk, timeout: Character.objects.get(pk=pk),
)
@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(TASKS_PATH + ".MEMBERAUDIT_LOG_UPDATE_STATS", False)
@patch(MODELS_PATH + ".character.MEMBERAUDIT_DATA_RETENTION_LIMIT", None)
@patch(MODELS_PATH + ".character.esi")
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestUpdateAllCharacters(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)

    def test_normal(self, mock_esi):
        mock_esi.client = esi_client_stub

        update_all_characters()
        self.assertTrue(self.character_1001.is_update_status_ok())


@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(TASKS_PATH + ".Location.objects.structure_update_or_create_esi")
class TestUpdateStructureEsi(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character = create_memberaudit_character(1001)
        cls.token = cls.character.character_ownership.user.token_set.first()

    def test_normal(self, mock_structure_update_or_create_esi):
        """When ESI status is ok, then create MailEntity"""
        mock_structure_update_or_create_esi.return_value = None
        try:
            update_structure_esi(id=1000000000001, token_pk=self.token.pk)
        except Exception as ex:
            self.fail(f"Unexpected exception occurred: {ex}")

    def test_invalid_token(self, mock_structure_update_or_create_esi):
        """When called with invalid token, raise exception"""
        mock_structure_update_or_create_esi.side_effect = EsiOffline

        with self.assertRaises(Token.DoesNotExist):
            update_structure_esi(id=1000000000001, token_pk=generate_invalid_pk(Token))

    def test_esi_status_1(self, mock_structure_update_or_create_esi):
        """When ESI is offline, then retry"""
        mock_structure_update_or_create_esi.side_effect = EsiOffline

        with self.assertRaises(CeleryRetry):
            update_structure_esi(id=1000000000001, token_pk=self.token.pk)

    def test_esi_status_2(self, mock_structure_update_or_create_esi):
        """When ESI error limit reached, then retry"""
        mock_structure_update_or_create_esi.side_effect = EsiErrorLimitExceeded(5)

        with self.assertRaises(CeleryRetry):
            update_structure_esi(id=1000000000001, token_pk=self.token.pk)


@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@patch(TASKS_PATH + ".MailEntity.objects.update_or_create_esi")
class TestUpdateMailEntityEsi(TestCase):
    def test_normal(self, mock_update_or_create_esi):
        """When ESI status is ok, then create MailEntity"""
        mock_update_or_create_esi.return_value = None
        try:
            update_mail_entity_esi(1001)
        except Exception:
            self.fail("Unexpected exception occurred")

    def test_esi_status_1(self, mock_update_or_create_esi):
        """When ESI is offline, then retry"""
        mock_update_or_create_esi.side_effect = EsiOffline

        with self.assertRaises(CeleryRetry):
            update_mail_entity_esi(1001)

    def test_esi_status_2(self, mock_update_or_create_esi):
        """When ESI error limit reached, then retry"""
        mock_update_or_create_esi.side_effect = EsiErrorLimitExceeded(5)

        with self.assertRaises(CeleryRetry):
            update_mail_entity_esi(1001)


@patch(TASKS_PATH + ".fetch_esi_status", lambda: EsiStatus(True, 99, 60))
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestUpdateCharactersDoctrines(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def setUp(self) -> None:
        self.character_1001 = create_memberaudit_character(1001)

    @patch(MODELS_PATH + ".character.Character.update_skill_sets")
    def test_normal(self, mock_update_skill_sets):
        update_characters_skill_checks()
        self.assertTrue(mock_update_skill_sets.called)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestDeleteCharacter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()

    def test_should_delete_a_character(self):
        # given
        character_1001 = create_memberaudit_character(1001)
        # when
        delete_character.delay(character_1001.pk)
        # then
        self.assertFalse(Character.objects.filter(pk=character_1001.pk).exists())


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestExportData(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_entities()
        cls.character = create_memberaudit_character(1001)

    @patch(TASKS_PATH + ".data_exporters.export_topic_to_archive")
    def test_should_export_all_topics(self, mock_export_topic_to_file):
        # when
        export_data()
        # then
        called_topics = [
            call[1]["topic"] for call in mock_export_topic_to_file.call_args_list
        ]
        self.assertEqual(len(called_topics), 3)
        self.assertSetEqual(
            set(called_topics), {"contract", "contract-item", "wallet-journal"}
        )

    @patch(TASKS_PATH + ".data_exporters.export_topic_to_archive")
    def test_should_export_wallet_journal(self, mock_export_topic_to_file):
        # when
        _export_data_for_topic(topic="abc")
        # then
        self.assertTrue(mock_export_topic_to_file.called)
        _, kwargs = mock_export_topic_to_file.call_args
        self.assertEqual(kwargs["topic"], "abc")
