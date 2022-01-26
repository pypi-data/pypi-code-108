from datetime import timedelta
from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.utils.timezone import now
from eveuniverse.models import EveType

from allianceauth.timerboard.models import Timer as AuthTimer
from app_utils.django import app_labels
from app_utils.testing import NoSocketsTestCase

from ..models import Timer
from .testdata.factory import create_user
from .testdata.fixtures import LoadTestDataMixin

PACKAGE_PATH = "structuretimers.management.commands"
MODELS_PATH = "structuretimers.models"


@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@patch(MODELS_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
@patch(PACKAGE_PATH + ".structuretimers_migrate_timers.get_input")
class TestMigirateTimers(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if "timerboard" not in app_labels():
            raise KeyboardInterrupt(
                "App `timerboard` is not installed, which is required for this test"
            )

    def setUp(self) -> None:
        self.out = StringIO()
        self.user = create_user(self.character_1)
        self.auth_timer = AuthTimer.objects.create(
            system="Abune",
            planet_moon="Near Heydieles gate",
            structure="Astrahus",
            eve_time=now() + timedelta(hours=4),
            eve_character=self.character_1,
            eve_corp=self.corporation_1,
            user=self.user,
        )
        Timer.objects.all().delete()

    def test_full_armor_friendly(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.details = "Armor timer"
        self.auth_timer.objective = "Friendly"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        new_timer = Timer.objects.first()
        self.assertEqual(new_timer.eve_solar_system, self.system_abune)
        self.assertEqual(new_timer.structure_type, self.type_astrahus)
        self.assertEqual(new_timer.timer_type, Timer.Type.ARMOR)
        self.assertEqual(new_timer.details_notes, "Armor timer")
        self.assertEqual(new_timer.objective, Timer.Objective.FRIENDLY)
        self.assertEqual(new_timer.date, self.auth_timer.eve_time)
        self.assertEqual(new_timer.eve_character, self.character_1)
        self.assertEqual(new_timer.eve_corporation, self.corporation_1)
        self.assertEqual(new_timer.user, self.auth_timer.user)

    def test_hull_hostile(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.details = "Hull timer"
        self.auth_timer.objective = "Hostile"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        new_timer = Timer.objects.first()
        self.assertEqual(new_timer.timer_type, Timer.Type.HULL)
        self.assertEqual(new_timer.objective, Timer.Objective.HOSTILE)

    def test_anchoring(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.details = "Anchor timer"
        self.auth_timer.objective = "Neutral"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        new_timer = Timer.objects.first()
        self.assertEqual(new_timer.timer_type, Timer.Type.ANCHORING)
        self.assertEqual(new_timer.objective, Timer.Objective.NEUTRAL)

    def test_final_corp_timer(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.details = "Final timer"
        self.auth_timer.corp_timer = True
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        new_timer = Timer.objects.first()
        self.assertEqual(new_timer.timer_type, Timer.Type.FINAL)
        self.assertEqual(new_timer.visibility, Timer.Visibility.CORPORATION)

    def test_moon_mining(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.structure = "Moon Mining Cycle"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        new_timer = Timer.objects.first()
        self.assertEqual(new_timer.timer_type, Timer.Type.MOONMINING)
        self.assertEqual(new_timer.structure_type, EveType.objects.get(id=35835))

    def test_abort_on_unknown_solar_system(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.system = "Unknown"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        self.assertFalse(Timer.objects.all().exists())

    def test_abort_on_unknown_structure_type(self, mock_get_input):
        mock_get_input.return_value = "Y"
        self.auth_timer.structure = "Unknown"
        self.auth_timer.save()

        call_command("structuretimers_migrate_timers", stdout=self.out)

        self.assertFalse(Timer.objects.all().exists())

    def test_do_not_create_duplicates(self, mock_get_input):
        mock_get_input.return_value = "Y"

        call_command("structuretimers_migrate_timers", stdout=self.out)
        call_command("structuretimers_migrate_timers", stdout=self.out)

        self.assertEqual(Timer.objects.all().count(), 1)
