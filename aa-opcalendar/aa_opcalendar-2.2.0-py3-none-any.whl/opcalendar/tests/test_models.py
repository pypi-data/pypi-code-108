import datetime as dt
from unittest.mock import patch

from pytz import utc

from allianceauth.tests.auth_utils import AuthUtils

from ..models import IngameEvents, EventCategory, EventHost, Owner
from .testdata import (
    esi_get_characters_character_id_calendar,
    esi_get_characters_character_id_calendar_event_id,
)
from ..utils import NoSocketsTestCase, add_character_to_user_2, add_new_token


MODULE_PATH = "opcalendar.models"


@patch(MODULE_PATH + ".esi")
class TestOwnerUpdateEventsEsi(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = AuthUtils.create_user("Bruce Wayne")
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "opcalendar.add_ingame_calendar_owner", cls.user
        )
        cls.eve_character = add_character_to_user_2(
            cls.user, 1001, "Bruce Wayne", 2001, "Wayne Technologies"
        )
        add_new_token(
            cls.user, cls.eve_character, ["esi-calendar.read_calendar_events.v1"]
        )
        cls.host = EventHost.objects.create(community="Test Host")
        cls.category = EventCategory.objects.create(
            name="NPSI", ticker="NPSI", color=EventCategory.COLOR_PURPLE
        )
        cls.owner = Owner.objects.create(
            character=cls.user.character_ownerships.first()
        )

    def test_should_add_new_events(self, mock_esi):
        # given
        mock_esi.client.Calendar.get_characters_character_id_calendar = (
            esi_get_characters_character_id_calendar
        )
        mock_esi.client.Calendar.get_characters_character_id_calendar_event_id = (
            esi_get_characters_character_id_calendar_event_id
        )
        # when
        self.owner.update_events_esi()
        # then
        self.assertEqual(IngameEvents.objects.count(), 1)
        obj = IngameEvents.objects.first()
        self.assertEqual(obj.event_id, 1386435)
        self.assertEqual(obj.owner, self.owner)
        self.assertEqual(obj.text, "The EVE Online Show features latest developer news")
        self.assertEqual(obj.owner_name, "EVE System")
        self.assertEqual(obj.owner_type, "eve_server")
        self.assertEqual(obj.importance, "1")
        self.assertEqual(obj.duration, "60")
        self.assertEqual(
            obj.event_start_date, utc.localize(dt.datetime(2016, 6, 26, 21, 0))
        )
        self.assertEqual(
            obj.event_end_date, utc.localize(dt.datetime(2016, 6, 26, 22, 0))
        )
        self.assertEqual(obj.title, "o7 The EVE Online Show")

    def test_should_not_replace_existing_events(self, mock_esi):
        # given
        mock_esi.client.Calendar.get_characters_character_id_calendar = (
            esi_get_characters_character_id_calendar
        )
        mock_esi.client.Calendar.get_characters_character_id_calendar_event_id = (
            esi_get_characters_character_id_calendar_event_id
        )
        original_event = IngameEvents.objects.create(
            event_id=1386435,
            event_start_date=utc.localize(dt.datetime(2016, 6, 26, 21, 0)),
            event_end_date=utc.localize(dt.datetime(2016, 6, 26, 22, 0)),
            owner=self.owner,
            text="The EVE Online Show features latest developer news",
            owner_type="eve_server",
            owner_name="EVE Server",
            importance="1",
            duration="30",
        )
        # when
        self.owner.update_events_esi()
        # then
        self.assertEqual(IngameEvents.objects.count(), 1)
        self.assertTrue(IngameEvents.objects.filter(pk=original_event.pk).exists())
