import datetime as dt
from unittest.mock import patch

from pytz import utc
import requests
import requests_mock


from allianceauth.tests.auth_utils import AuthUtils

from ..models import Event, EventCategory, EventHost, EventImport
from .. import tasks
from .testdata import feedparser_parse, generate_ical_string
from ..utils import NoSocketsTestCase

MODULE_PATH = "opcalendar.tasks"


@patch(MODULE_PATH + ".feedparser")
@requests_mock.Mocker()
class TestImportNpsiFleet(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = AuthUtils.create_user("Bruce Wayne")
        cls.eve_character = AuthUtils.add_main_character_2(
            cls.user, "Bruce Wayne", 1001, 2001
        )
        cls.host = EventHost.objects.create(community="Test Host")
        cls.category = EventCategory.objects.create(
            name="NPSI", ticker="NPSI", color=EventCategory.COLOR_PURPLE
        )

    ########################
    # spectre fleets only

    def test_should_add_new_spectre_fleet_event(self, mock_feedparser, requests_mocker):
        # given
        mock_feedparser.parse = feedparser_parse
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        obj = Event.objects.first()
        self.assertEqual(obj.operation_type, self.category)
        self.assertEqual(obj.title, "Spectre Fleet 1")
        self.assertEqual(obj.host, self.host)
        self.assertEqual(obj.doctrine, "see details")
        self.assertEqual(obj.formup_system, EventImport.SPECTRE_FLEET)
        self.assertEqual(obj.description, "")
        published = utc.localize(dt.datetime(2021, 2, 5, 21, 0))
        self.assertEqual(obj.start_time, published)
        self.assertEqual(obj.end_time, published)
        self.assertEqual(obj.fc, EventImport.SPECTRE_FLEET)
        self.assertEqual(obj.visibility, Event.VISIBILITY_EXTERNAL)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.eve_character, self.eve_character)

    def test_should_add_new_spectre_fleet_event_no_character(
        self, mock_feedparser, requests_mocker
    ):
        # given
        mock_feedparser.parse = feedparser_parse
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertTrue(Event.objects.filter(title="Spectre Fleet 1").exists())

    def test_should_not_replace_existing_spectre_fleet_event(
        self, mock_feedparser, requests_mocker
    ):
        # given
        mock_feedparser.parse = feedparser_parse
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        published = utc.localize(dt.datetime(2021, 2, 5, 21, 0))
        original_event = Event.objects.create(
            operation_type=self.category,
            title="Spectre Fleet 1",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.SPECTRE_FLEET,
            description="Testing Eve Uni class 1",
            start_time=published,
            end_time=published,
            fc=EventImport.SPECTRE_FLEET,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        self.assertTrue(Event.objects.filter(pk=original_event.pk).exists())

    def test_should_delete_outdated_spectre_fleet_event(
        self, mock_feedparser, requests_mocker
    ):
        # given
        mock_feedparser.parse = lambda x: feedparser_parse("no-data")
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        published = utc.localize(dt.datetime(2021, 2, 3, 21, 0))
        Event.objects.create(
            operation_type=self.category,
            title="Spectre Fleet OLD",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.SPECTRE_FLEET,
            description="Testing Eve Uni class OLD",
            start_time=published,
            end_time=published,
            fc=EventImport.SPECTRE_FLEET,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 0)

    def test_should_report_when_spectre_fleet_has_error(
        self, mock_feedparser, requests_mocker
    ):
        # given
        mock_feedparser.parse.side_effect = RuntimeError
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        result = tasks.import_all_npsi_fleets()
        # then
        self.assertFalse(result)
        self.assertEqual(Event.objects.count(), 0)

    ########################
    # fun inc only

    def test_should_add_new_fun_inc_event(self, mock_feedparser, requests_mocker):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text=generate_ical_string("fun_inc"),
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        obj = Event.objects.first()
        self.assertEqual(obj.operation_type, self.category)
        self.assertEqual(obj.title, "Fun Fleet 1")
        self.assertEqual(obj.host, self.host)
        self.assertEqual(obj.doctrine, "see details")
        self.assertEqual(obj.formup_system, EventImport.FUN_INC)
        self.assertEqual(obj.description, "Testing Fun Fleet 1")
        self.assertEqual(obj.start_time, utc.localize(dt.datetime(2021, 2, 5, 22, 0)))
        self.assertEqual(obj.end_time, utc.localize(dt.datetime(2021, 2, 5, 23, 0)))
        self.assertEqual(obj.fc, EventImport.FUN_INC)
        self.assertEqual(obj.visibility, Event.VISIBILITY_EXTERNAL)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.eve_character, self.eve_character)

    def test_should_add_new_fun_inc_event_no_character(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text=generate_ical_string("fun_inc"),
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertTrue(Event.objects.filter(title="Fun Fleet 1").exists())

    def test_should_not_replace_existing_fun_inc_event(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text=generate_ical_string("fun_inc"),
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        original_event = Event.objects.create(
            operation_type=self.category,
            title="Fun Fleet 1",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.FUN_INC,
            description="Testing Fun Fleet 1",
            start_time=utc.localize(dt.datetime(2021, 2, 5, 22, 0)),
            end_time=utc.localize(dt.datetime(2021, 2, 5, 23, 0)),
            fc=EventImport.FUN_INC,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        self.assertTrue(Event.objects.filter(pk=original_event.pk).exists())

    def test_should_delete_outdated_fun_inc_event(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text=generate_ical_string("no-data"),
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        Event.objects.create(
            operation_type=self.category,
            title="Fun Fleet OLD",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.FUN_INC,
            description="Testing Fun Fleet OLD",
            start_time=utc.localize(dt.datetime(2021, 2, 4, 22, 0)),
            end_time=utc.localize(dt.datetime(2021, 2, 4, 23, 0)),
            fc=EventImport.FUN_INC,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 0)

    def test_should_report_when_fun_inc_calendar_is_invalid(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text="",
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        result = tasks.import_all_npsi_fleets()
        # then
        self.assertFalse(result)
        self.assertEqual(Event.objects.count(), 0)

    def test_should_report_when_fun_inc_calendar_request_has_error(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            exc=requests.exceptions.ConnectTimeout,
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        result = tasks.import_all_npsi_fleets()
        # then
        self.assertFalse(result)
        self.assertEqual(Event.objects.count(), 0)

    ########################
    # eve uni only

    def test_should_add_new_eve_uni_event(self, mock_feedparser, requests_mocker):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            text=generate_ical_string("eve_uni"),
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        obj = Event.objects.first()
        self.assertEqual(obj.operation_type, self.category)
        self.assertEqual(obj.title, "Eve Uni class 1")
        self.assertEqual(obj.host, self.host)
        self.assertEqual(obj.doctrine, "see details")
        self.assertEqual(obj.formup_system, EventImport.EVE_UNIVERSITY)
        self.assertEqual(obj.description, "Testing Eve Uni class 1")
        self.assertEqual(obj.start_time, utc.localize(dt.datetime(2021, 2, 4, 22, 0)))
        self.assertEqual(obj.end_time, utc.localize(dt.datetime(2021, 2, 4, 23, 0)))
        self.assertEqual(obj.fc, EventImport.EVE_UNIVERSITY)
        self.assertEqual(obj.visibility, Event.VISIBILITY_EXTERNAL)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.eve_character, self.eve_character)

    def test_should_add_new_eve_uni_event_no_character(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            text=generate_ical_string("eve_uni"),
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertTrue(Event.objects.filter(title="Eve Uni class 1").exists())

    def test_should_not_replace_existing_eve_uni_event(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            text=generate_ical_string("eve_uni"),
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        original_event = Event.objects.create(
            operation_type=self.category,
            title="Eve Uni class 1",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.EVE_UNIVERSITY,
            description="Testing Eve Uni class 1",
            start_time=utc.localize(dt.datetime(2021, 2, 4, 22, 0)),
            end_time=utc.localize(dt.datetime(2021, 2, 4, 23, 0)),
            fc=EventImport.EVE_UNIVERSITY,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 1)
        self.assertTrue(Event.objects.filter(pk=original_event.pk).exists())

    def test_should_delete_outdated_eve_uni_events(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            text=generate_ical_string("no-data"),
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        Event.objects.create(
            operation_type=self.category,
            title="Eve Uni class OLD",
            host=self.host,
            doctrine="see details",
            formup_system=EventImport.EVE_UNIVERSITY,
            description="Testing Eve Uni class OLD",
            start_time=utc.localize(dt.datetime(2021, 2, 3, 22, 0)),
            end_time=utc.localize(dt.datetime(2021, 2, 3, 23, 0)),
            fc=EventImport.EVE_UNIVERSITY,
            external=True,
            user=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 0)

    def test_should_report_when_eve_uni_request_has_error(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            exc=requests.exceptions.ConnectTimeout,
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        result = tasks.import_all_npsi_fleets()
        # then
        self.assertFalse(result)
        self.assertEqual(Event.objects.count(), 0)

    def test_should_report_when_eve_uni_calendar_is_invalid(
        self, mock_feedparser, requests_mocker
    ):
        # given
        requests_mocker.register_uri(
            "GET", url="https://portal.eveuniversity.org/api/getcalendar", text=""
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        result = tasks.import_all_npsi_fleets()
        # then
        self.assertFalse(result)
        self.assertEqual(Event.objects.count(), 0)

    ########################
    # multiple fleet types

    def test_should_add_fleet_events_all_types(self, mock_feedparser, requests_mocker):
        # given
        mock_feedparser.parse = feedparser_parse
        EventImport.objects.create(
            source=EventImport.SPECTRE_FLEET,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        requests_mocker.register_uri(
            "GET",
            url="https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics",
            text=generate_ical_string("fun_inc"),
        )
        EventImport.objects.create(
            source=EventImport.FUN_INC,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        requests_mocker.register_uri(
            "GET",
            url="https://portal.eveuniversity.org/api/getcalendar",
            text=generate_ical_string("eve_uni"),
        )
        EventImport.objects.create(
            source=EventImport.EVE_UNIVERSITY,
            host=self.host,
            operation_type=self.category,
            creator=self.user,
            eve_character=self.eve_character,
        )
        # when
        tasks.import_all_npsi_fleets()
        # then
        self.assertEqual(Event.objects.count(), 3)
        self.assertTrue(Event.objects.filter(title="Spectre Fleet 1").exists())
        self.assertTrue(Event.objects.filter(title="Fun Fleet 1").exists())
        self.assertTrue(Event.objects.filter(title="Eve Uni class 1").exists())
