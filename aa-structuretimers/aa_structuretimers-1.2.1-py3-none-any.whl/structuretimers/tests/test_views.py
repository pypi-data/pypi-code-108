from datetime import timedelta
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from app_utils.testing import (
    create_user_from_evecharacter,
    json_response_to_dict,
    json_response_to_python,
)

from ..models import Timer
from .testdata.factory import create_staging_system, create_timer, create_user
from .testdata.fixtures import LoadTestDataMixin
from .utils import add_permission_to_user_by_name

MODELS_PATH = "structuretimers.models"


@patch(MODELS_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestViewBase(LoadTestDataMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # user
        cls.user_1 = create_user(cls.character_1)
        cls.user_2 = create_user(cls.character_2)
        cls.user_2 = add_permission_to_user_by_name(
            "structuretimers.manage_timer", cls.user_2
        )
        cls.user_3 = create_user(cls.character_3)
        # timers
        with patch(MODELS_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False):
            cls.timer_1 = create_timer(
                structure_name="Timer 1",
                location_details="Near the star",
                date=now() + timedelta(hours=4),
                eve_character=cls.character_1,
                eve_corporation=cls.corporation_1,
                user=cls.user_1,
                eve_solar_system=cls.system_abune,
                structure_type=cls.type_astrahus,
                owner_name="Big Boss",
                details_image_url="http://www.example.com/dummy.png",
                details_notes="Some notes",
            )
            cls.timer_2 = create_timer(
                structure_name="Timer 2",
                date=now() - timedelta(hours=8),
                eve_character=cls.character_1,
                eve_corporation=cls.corporation_1,
                user=cls.user_1,
                eve_solar_system=cls.system_abune,
                structure_type=cls.type_raitaru,
                is_important=True,
            )
            cls.timer_3 = create_timer(
                structure_name="Timer 3",
                date=now() - timedelta(hours=8),
                eve_character=cls.character_1,
                eve_corporation=cls.corporation_1,
                user=cls.user_1,
                eve_solar_system=cls.system_enaluri,
                structure_type=cls.type_astrahus,
            )
            cls.timer_4 = create_timer(
                timer_type=Timer.Type.PRELIMINARY,
                structure_name="Timer 4",
                eve_character=cls.character_1,
                eve_corporation=cls.corporation_1,
                user=cls.user_1,
            )


class TestListViewWithSelectedStagingSystem(TestViewBase):
    def test_should_open_with_main_staging_system(self):
        # given
        create_staging_system(eve_solar_system=self.system_abune)
        staging_system = create_staging_system(
            eve_solar_system=self.system_enaluri, light_years=1.2, jumps=3, is_main=True
        )
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["selected_staging_system"], staging_system
        )

    def test_should_open_with_first_staging_system(self):
        # given
        staging_system = create_staging_system(
            eve_solar_system=self.system_enaluri, light_years=1.2, jumps=3
        )
        create_staging_system(eve_solar_system=self.system_abune)
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["selected_staging_system"], staging_system
        )

    def test_should_open_without_staging_system(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context_data["selected_staging_system"])

    def test_should_ignore_wrong_staging_system_name(self):
        # given
        staging_system = create_staging_system(
            eve_solar_system=self.system_enaluri, light_years=1.2, jumps=3, is_main=True
        )
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/?staging=invalid_name")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["selected_staging_system"], staging_system
        )

    def test_should_handle_multiple_invalid_staging_systems(self):
        # given
        create_staging_system()
        create_staging_system()
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context_data["selected_staging_system"])

    def test_should_handle_multiple_invalid_staging_systems_with_main(self):
        # given
        create_staging_system(is_main=True)
        create_staging_system()
        self.client.force_login(self.user_1)
        # when
        response = self.client.get("/structuretimers/")
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context_data["selected_staging_system"])


class TestListData(TestViewBase):
    def _get_timer_list_data(self, tab_name: str = "current", user: User = None):
        if not user:
            user = self.user_1
        self.client.force_login(user)
        return self.client.get(
            reverse("structuretimers:timer_list_data", args=[tab_name])
        )

    def _get_timer_list_data_ids(
        self, tab_name: str = "current", user: User = None
    ) -> set:
        response = self._get_timer_list_data(tab_name, user)
        self.assertEqual(response.status_code, 200)
        return set(json_response_to_dict(response).keys())

    # def test_timer_list_view_loads(self):
    #     request = self.factory.get(reverse("structuretimers:timer_list"))
    #     request.user = self.user_1
    #     response = views.timer_list(request)
    #     self.assertEqual(response.status_code, 200)

    def test_return_current_timers(self):
        # when
        timer_ids = self._get_timer_list_data_ids("current")
        # then
        self.assertSetEqual(timer_ids, {self.timer_1.id})

    def test_return_past_timers(self):
        # when
        timer_ids = self._get_timer_list_data_ids("past")
        # then
        self.assertSetEqual(timer_ids, {self.timer_2.id, self.timer_3.id})

    def test_return_preliminary_timers(self):
        # when
        timer_ids = self._get_timer_list_data_ids("preliminary")
        # then
        self.assertSetEqual(timer_ids, {self.timer_4.id})

    def test_should_require_permission(self):
        # given
        user, _ = create_user_from_evecharacter(1003)
        self.client.force_login(user)
        # when
        response = self.client.get(
            reverse("structuretimers:timer_list_data", args=["current"])
        )
        # then
        self.assertEqual(response.status_code, 302)

    def test_show_corp_restricted_to_corp_member(self):
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_2,
            visibility=Timer.Visibility.CORPORATION,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_corp_restricted_to_non_corp_member(self):
        create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            visibility=Timer.Visibility.CORPORATION,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_alliance_restricted_to_alliance_member(self):
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_alliance=self.alliance_1,
            user=self.user_2,
            visibility=Timer.Visibility.ALLIANCE,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_alliance_restricted_to_non_alliance_member(self):
        create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            eve_alliance=self.alliance_3,
            user=self.user_3,
            visibility=Timer.Visibility.ALLIANCE,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_opsec_restricted_to_opsec_member(self):
        self.user_1 = add_permission_to_user_by_name(
            "structuretimers.opsec_access", self.user_1
        )
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_opsec_restricted_to_non_opsec_member(self):
        create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_opsec_corp_restricted_to_opsec_member_other_corp(self):
        self.user_1 = add_permission_to_user_by_name(
            "structuretimers.opsec_access", self.user_1
        )
        create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
            visibility=Timer.Visibility.CORPORATION,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_corp_timer_to_creator_of_different_corp(self):
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            visibility=Timer.Visibility.CORPORATION,
            user=self.user_1,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_alliance_timer_to_creator_of_different_alliance(self):
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_alliance=self.alliance_3,
            eve_corporation=self.corporation_3,
            visibility=Timer.Visibility.ALLIANCE,
            user=self.user_1,
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_can_show_timers_without_user_character_corporation_or_alliance(self):
        timer_4 = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
        )
        timer_ids = self._get_timer_list_data_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_list_for_manager(self):
        timer_ids = self._get_timer_list_data_ids(user=self.user_2)
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_should_include_distances_1(self):
        # given
        timer = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_alliance=self.alliance_3,
            eve_corporation=self.corporation_3,
            user=self.user_1,
        )
        staging_system = create_staging_system(
            eve_solar_system=self.system_enaluri,
            light_years=1.2,
            jumps=3,
        )
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:timer_list_data", args=["current"])
            + f"?staging={staging_system.pk}"
        )
        # then
        data = json_response_to_dict(response)
        obj = data[timer.id]
        self.assertEqual(obj["distance_light_years"], 1.2)
        self.assertEqual(obj["distance_jumps"], 3)
        self.assertTrue(obj["distance"])

    def test_should_not_include_distances_1(self):
        # given
        timer = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_alliance=self.alliance_3,
            eve_corporation=self.corporation_3,
            user=self.user_1,
        )
        create_staging_system(
            eve_solar_system=self.system_enaluri, light_years=1.2, jumps=3, is_main=True
        )
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:timer_list_data", args=["current"])
        )
        # then
        data = json_response_to_dict(response)
        obj = data[timer.id]
        self.assertIsNone(obj["distance_light_years"])
        self.assertIsNone(obj["distance_jumps"])

    def test_should_not_include_distances_2(self):
        # given
        timer = create_timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_alliance=self.alliance_3,
            eve_corporation=self.corporation_3,
            user=self.user_1,
        )
        staging_system = create_staging_system(eve_solar_system=self.system_enaluri)
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:timer_list_data", args=["current"])
            + f"?staging={staging_system.pk}"
        )
        # then
        data = json_response_to_dict(response)
        obj = data[timer.id]
        self.assertIsNone(obj["distance_light_years"])
        self.assertIsNone(obj["distance_jumps"])


@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
class TestDetailView(TestViewBase):
    def test_should_return_normal_timer(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:detail", args=[self.timer_1.pk])
        )
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn("Timer 1", response.rendered_content)

    def test_should_return_preliminary_timer(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:detail", args=[self.timer_4.pk])
        )
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn("Timer 4", response.rendered_content)

    def test_forbidden(self):
        # given
        self.client.force_login(self.user_1)
        self.timer_1.is_opsec = True
        self.timer_1.save()
        # when
        response = self.client.get(
            reverse("structuretimers:detail", args=[self.timer_1.pk])
        )
        # then
        self.assertEqual(response.status_code, 302)


class TestSelect2Views(LoadTestDataMixin, TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = create_user(cls.character_1)

    def test_should_return_solar_systems(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:select2_solar_systems"), data={"term": "abu"}
        )
        # then
        self.assertEqual(response.status_code, 200)
        data = json_response_to_python(response)
        self.assertEqual(data, {"results": [{"id": 30004984, "text": "Abune"}]})

    def test_should_return_empty_solar_system_list(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(reverse("structuretimers:select2_solar_systems"))
        # then
        self.assertEqual(response.status_code, 200)
        data = json_response_to_python(response)
        self.assertEqual(data, {"results": None})

    def test_should_return_structure_types(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(
            reverse("structuretimers:select2_structure_types"), data={"term": "ast"}
        )
        # then
        self.assertEqual(response.status_code, 200)
        data = json_response_to_python(response)
        self.assertEqual(data, {"results": [{"id": 35832, "text": "Astrahus"}]})

    def test_should_return_empty_struture_types_list(self):
        # given
        self.client.force_login(self.user_1)
        # when
        response = self.client.get(reverse("structuretimers:select2_structure_types"))
        # then
        self.assertEqual(response.status_code, 200)
        data = json_response_to_python(response)
        self.assertEqual(data, {"results": None})
