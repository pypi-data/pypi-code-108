# Django
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import add_character_to_user, create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import AFat, AFatLink
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.views.dashboard import overview

MODULE_PATH = "afat.views.dashboard"


def response_content_to_str(response) -> str:
    return response.content.decode(response.charset)


class TestDashboard(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user, _ = create_user_from_evecharacter(
            cls.character_1001.character_id, permissions=["afat.basic_access"]
        )

        add_character_to_user(cls.user, cls.character_1101)

        create_user_from_evecharacter(cls.character_1002.character_id)

        cls.afat_link = AFatLink.objects.create(
            fleet="Demo Fleet",
            hash="123",
            creator=cls.user,
            character=cls.character_1001,
        )

    def _page_overview_request(self, user):
        request = self.factory.get(reverse("afat:dashboard"))
        request.user = user

        middleware = SessionMiddleware()
        middleware.process_request(request)

        return overview(request)

    # def test_should_open_page_normally(self):
    #     # when
    #     response = self._page_request(self.user)
    #
    #     # then
    #     self.assertEqual(response.status_code, 200)

    def test_should_only_show_my_chars_and_only_those_with_fat_links(self):
        # given
        AFat.objects.create(character=self.character_1101, afatlink=self.afat_link)
        AFat.objects.create(character=self.character_1002, afatlink=self.afat_link)

        # when
        response = self._page_overview_request(self.user)

        # then
        content = response_content_to_str(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'<span id="afat-eve-character-id-{self.character_1101.character_id}">{self.character_1101.character_name}</span>',
            content,
        )
        self.assertNotIn(
            f'<span id="afat-eve-character-id-{self.character_1001.character_id}">{self.character_1001.character_name}</span>',
            content,
        )
        self.assertNotIn(
            f'<span id="afat-eve-character-id-{self.character_1002.character_id}">{self.character_1002.character_name}</span>',
            content,
        )
