# Standard Library
import datetime as dt

# Third Party
from pytz import utc

# Django
from django.test import TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import add_character_to_user, create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import AFat, AFatLink
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.tests.fixtures.utils import RequestStub
from afat.views.statistics import _calculate_year_stats

MODULE_PATH = "afat.views.statistics"


def response_content_to_str(response) -> str:
    return response.content.decode(response.charset)


class TestStatistics(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1003 = EveCharacter.objects.get(character_id=1003)
        cls.character_1004 = EveCharacter.objects.get(character_id=1004)
        cls.character_1005 = EveCharacter.objects.get(character_id=1005)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user_without_access, _ = create_user_from_evecharacter(
            cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            cls.character_1002.character_id, permissions=["afat.basic_access"]
        )

        add_character_to_user(cls.user_with_basic_access, cls.character_1101)

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            cls.character_1003.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        cls.user_with_stats_corporation_other, _ = create_user_from_evecharacter(
            cls.character_1004.character_id,
            permissions=["afat.basic_access", "afat.stats_corporation_other"],
        )

        cls.user_with_stats_corporation_own, _ = create_user_from_evecharacter(
            cls.character_1005.character_id,
            permissions=["afat.basic_access", "afat.stats_corporation_own"],
        )

        # Generate some FAT links and FATs
        afat_link_april_1 = AFatLink.objects.create(
            fleet="April Fleet 1",
            hash="1231",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 1, tzinfo=utc),
        )
        afat_link_april_2 = AFatLink.objects.create(
            fleet="April Fleet 2",
            hash="1232",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 15, tzinfo=utc),
        )
        afat_link_september = AFatLink.objects.create(
            fleet="September Fleet",
            hash="1233",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 9, 1, tzinfo=utc),
        )

        AFat.objects.create(
            character=cls.character_1101, afatlink=afat_link_april_1, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1001, afatlink=afat_link_april_1, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1002, afatlink=afat_link_april_1, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1003, afatlink=afat_link_april_1, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1004, afatlink=afat_link_april_1, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1005, afatlink=afat_link_april_1, shiptype="Omen"
        )

        AFat.objects.create(
            character=cls.character_1101, afatlink=afat_link_april_2, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1004, afatlink=afat_link_april_2, shiptype="Thorax"
        )
        AFat.objects.create(
            character=cls.character_1002, afatlink=afat_link_april_2, shiptype="Thorax"
        )
        AFat.objects.create(
            character=cls.character_1003, afatlink=afat_link_april_2, shiptype="Omen"
        )

        AFat.objects.create(
            character=cls.character_1001, afatlink=afat_link_september, shiptype="Omen"
        )
        AFat.objects.create(
            character=cls.character_1004,
            afatlink=afat_link_september,
            shiptype="Guardian",
        )
        AFat.objects.create(
            character=cls.character_1005, afatlink=afat_link_september, shiptype="Omen"
        )

    def test_should_only_show_my_chars_and_only_those_with_fat_links(self):
        # when
        result = _calculate_year_stats(RequestStub(self.user_with_basic_access), 2020)

        # then
        self.assertListEqual(
            result, [("Clark Kent", {4: 2}, 1002), ("Lex Luther", {4: 2}, 1101)]
        )

    def test_should_show_statistics_dashboard(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:statistics_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_statistics_dashboard_for_year(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:statistics_overview", kwargs={"year": 2020})
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_statistics_dashboard_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse("afat:statistics_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_statistics_dashboard_for_user_with_stats_corporation_own(self):
        # given
        self.client.force_login(self.user_with_stats_corporation_own)

        # when
        url = reverse("afat:statistics_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_statistics_dashboard_for_user_without_access(self):
        # given
        self.client.force_login(self.user_without_access)

        # when
        url = reverse("afat:statistics_overview")
        res = self.client.get(url)

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res.url, "/account/login/?next=/fleet-activity-tracking/statistics/"
        )

    def test_should_show_own_character_stats(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse(
            "afat:statistics_character",
            kwargs={
                "charid": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    # def test_should_show_character_stats_for_user_with_stats_char_other(self):
    #     # given
    #     self.client.force_login(self.user_with_stats_corporation_other)
    #
    #     # when
    #     url = reverse(
    #         "afat:statistics_character",
    #         kwargs={
    #             "charid": self.user_with_basic_access.profile.main_character.character_id,
    #             "year": 2020,
    #             "month": 4,
    #         },
    #     )
    #     res = self.client.get(url)
    #
    #     # then
    #     self.assertEqual(res.status_code, 200)

    def test_should_show_own_corp_stats_for_user_with_stats_corporation_own(self):
        # given
        self.client.force_login(self.user_with_stats_corporation_own)

        # when
        url = reverse(
            "afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_stats_corporation_own.profile.main_character.corporation_id
            },
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_all_corp_stats_for_user_with_stats_corporation_other(self):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse(
            "afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_all_corp_stats_with_month_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse(
            "afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020, "month": 4},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_all_corp_stats_for_user_with_stats_corporation_own(self):
        # given
        self.client.force_login(self.user_with_stats_corporation_own)

        # when
        url = reverse("afat:statistics_corporation", kwargs={"corpid": 2002})
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, "/fleet-activity-tracking/")

    def test_should_show_all_alliance_stats_with_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse(
            "afat:statistics_alliance",
            kwargs={"allianceid": 3001},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_all_alliance_stats_with_year_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse(
            "afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_all_alliance_stats_with_month_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(self.user_with_stats_corporation_other)

        # when
        url = reverse(
            "afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020, "month": 4},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)
