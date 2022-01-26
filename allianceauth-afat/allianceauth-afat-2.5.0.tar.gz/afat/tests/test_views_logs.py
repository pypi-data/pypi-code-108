"""
Test logs view
"""

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
from app_utils.testing import create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import AFatLink
from afat.tests.fixtures.load_allianceauth import load_allianceauth

MODULE_PATH = "afat.views.logs"


class TestLogsView(TestCase):
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

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            cls.character_1003.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        cls.user_with_log_view, _ = create_user_from_evecharacter(
            cls.character_1004.character_id,
            permissions=["afat.basic_access", "afat.log_view"],
        )

        # cls.afat_link_type_cta = AFatLinkType.objects.create(name="CTA")
        # cls.afat_link_type_stratop = AFatLinkType.objects.create(name="Strat OP")

        # Generate some FAT links and FATs
        cls.afat_link_april_1 = AFatLink.objects.create(
            fleet="April Fleet 1",
            hash="1231",
            creator=cls.user_with_manage_afat,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 1, tzinfo=utc),
        )
        cls.afat_link_april_2 = AFatLink.objects.create(
            fleet="April Fleet 2",
            hash="1232",
            creator=cls.user_with_manage_afat,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 15, tzinfo=utc),
        )

    def test_should_not_show_log_view_for_user_without_access(self):
        # given
        self.client.force_login(self.user_without_access)

        # when
        url = reverse("afat:logs_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 302)

    def test_should_not_show_log_view_for_user_with_basic_access(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:logs_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 302)

    def test_should_show_log_view_for_user_with_manage_afat_permission(self):
        # given
        self.client.force_login(self.user_with_manage_afat)

        # when
        url = reverse("afat:logs_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_log_view_for_user_with_log_view_permission(self):
        # given
        self.client.force_login(self.user_with_log_view)

        # when
        url = reverse("afat:logs_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_ajax_get_logs(self):
        # given
        self.client.force_login(self.user_with_log_view)

        url = reverse("afat:logs_ajax_get_logs")
        result = self.client.get(url)

        # then
        self.assertEqual(result.status_code, 200)
