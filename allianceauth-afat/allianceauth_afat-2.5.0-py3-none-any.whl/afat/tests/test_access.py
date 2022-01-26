"""
Test access to the afat module
"""

# Django
from django.test import TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter

# Alliance Auth AFAT
from afat.tests.fixtures.load_allianceauth import load_allianceauth

MODULE_PATH = "afat.views.statistics"


class TestAccesss(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)

        cls.user_without_access, _ = create_user_from_evecharacter(
            cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            cls.character_1002.character_id, permissions=["afat.basic_access"]
        )

    def test_should_show_afat_dashboard_for_user_with_basic_access(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:dashboard")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_afat_dashboard_for_user_without_access(self):
        # given
        self.client.force_login(self.user_without_access)

        # when
        url = reverse("afat:dashboard")
        res = self.client.get(url)

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, "/account/login/?next=/fleet-activity-tracking/")
