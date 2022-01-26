import datetime as dt
import json
from unittest.mock import Mock, patch

import dhooks_lite
from pytz import utc

from django.core.cache import cache
from django.db import models
from django.test import TestCase, override_settings
from django.utils.timezone import now

from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo
from app_utils.json import JSONDateTimeDecoder
from app_utils.testing import NoSocketsTestCase

from .. import __title__
from ..models import (
    DiscordWebhook,
    NotificationRule,
    ScheduledNotification,
    StagingSystem,
    Timer,
    _task_calc_staging_system,
)
from .testdata.factory import (
    create_notification_rule,
    create_scheduled_notification,
    create_staging_system,
    create_timer,
    create_user,
)
from .testdata.fixtures import LoadTestDataMixin
from .utils import add_permission_to_user_by_name

MODULE_PATH = "structuretimers.models"


class TestTimer(LoadTestDataMixin, NoSocketsTestCase):
    def test_str_1(self):
        timer = Timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        expected = 'Armor timer for Raitaru "Test" in Abune @ 2020-08-06 13:25'
        self.assertEqual(str(timer), expected)

    def test_str_2(self):
        timer = Timer(
            structure_name="Test",
            timer_type=Timer.Type.PRELIMINARY,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
        )
        expected = 'Preliminary timer for Raitaru "Test" in Abune'
        self.assertEqual(str(timer), expected)

    def test_structure_display_name_1(self):
        timer = Timer(
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        expected = "Raitaru in Abune"
        self.assertEqual(timer.structure_display_name, expected)

    def test_structure_display_name_2(self):
        timer = Timer(
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            location_details="P5-M3",
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        expected = "Raitaru in Abune near P5-M3"
        self.assertEqual(timer.structure_display_name, expected)

    def test_structure_display_name_3(self):
        timer = Timer(
            structure_name="Big Boy",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        expected = 'Raitaru "Big Boy" in Abune'
        self.assertEqual(timer.structure_display_name, expected)

    def test_label_type_for_timer_type(self):
        timer = Timer(date=now())
        self.assertEqual(timer.label_type_for_timer_type(), "default")

        timer.timer_type = Timer.Type.ARMOR
        self.assertEqual(timer.label_type_for_timer_type(), "danger")

        timer.timer_type = Timer.Type.HULL
        self.assertEqual(timer.label_type_for_timer_type(), "danger")

    def test_label_type_for_objective(self):
        timer = Timer(date=now())
        self.assertEqual(timer.label_type_for_objective(), "default")

        timer.objective = Timer.Objective.HOSTILE
        self.assertEqual(timer.label_type_for_objective(), "danger")

        timer.objective = Timer.Objective.FRIENDLY
        self.assertEqual(timer.label_type_for_objective(), "primary")


@patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
class TestTimerSaveXScheduleNotifications(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )

    @patch(MODULE_PATH + "._task_schedule_notifications_for_timer")
    def test_schedule_notifications_for_new_timers(self, mock_schedule_notifications):
        timer = create_timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            enabled_notifications=True,
        )
        self.assertTrue(mock_schedule_notifications.called)
        _, kwargs = mock_schedule_notifications.return_value.apply_async.call_args
        self.assertEqual(kwargs["kwargs"]["timer_pk"], timer.pk)

    @patch(MODULE_PATH + "._task_schedule_notifications_for_timer")
    def test_dont_schedule_notifications_for_new_timers_when_turned_off(
        self, mock_schedule_notifications
    ):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        timer.save(disable_notifications=True)
        self.assertFalse(mock_schedule_notifications.called)

    def test_schedule_notifications_when_date_changed(self):
        with patch(
            MODULE_PATH + "._task_schedule_notifications_for_timer"
        ) as mock_schedule_notifications:
            timer = create_timer(
                date=now() + dt.timedelta(hours=4),
                eve_solar_system=self.system_abune,
                structure_type=self.type_astrahus,
            )

        with patch(
            MODULE_PATH + "._task_schedule_notifications_for_timer"
        ) as mock_schedule_notifications:
            timer.date = now() + dt.timedelta(hours=3)
            timer.save()
            self.assertTrue(mock_schedule_notifications.called)
            _, kwargs = mock_schedule_notifications.return_value.apply_async.call_args
            self.assertEqual(kwargs["kwargs"]["timer_pk"], timer.pk)

    def test_dont_schedule_notifications_else(self):
        with patch(
            MODULE_PATH + "._task_schedule_notifications_for_timer"
        ) as mock_schedule_notifications:
            timer = create_timer(
                date=now() + dt.timedelta(hours=4),
                eve_solar_system=self.system_abune,
                structure_type=self.type_astrahus,
            )

        with patch(
            MODULE_PATH + "._task_schedule_notifications_for_timer"
        ) as mock_schedule_notifications:
            timer.date = now() + dt.timedelta(hours=3)
            timer.structure_name = "Some fancy name"
            self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + "._task_schedule_notifications_for_timer")
    def test_dont_schedule_notifications_for_new_preliminary_timers(
        self, mock_schedule_notifications
    ):
        # when
        create_timer(timer_type=Timer.Type.PRELIMINARY)
        # then
        self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + "._task_schedule_notifications_for_timer")
    def test_remove_scheduled_notifications_when_timer_changed_to_prelimary(
        self, mock_schedule_notifications
    ):
        # given
        rule = create_notification_rule(is_enabled=False)
        timer = create_timer(date=now() + dt.timedelta(hours=4))
        notification = create_scheduled_notification(
            notification_rule=rule, timer=timer
        )
        mock_schedule_notifications.reset()
        # when
        timer.timer_type = Timer.Type.PRELIMINARY
        timer.save()
        # then
        self.assertFalse(mock_schedule_notifications.called)
        self.assertFalse(
            ScheduledNotification.objects.filter(pk=notification.pk).exists()
        )


@patch(MODULE_PATH + "._task_schedule_notifications_for_timer", Mock)
class TestTimerSaveXCalcDistances(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )

    @patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems")
    def test_should_calc_distances_when_created(self, mock_calc_distances):
        # when
        timer = Timer.objects.create(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        # then
        self.assertTrue(mock_calc_distances.called)
        _, kwargs = mock_calc_distances.return_value.apply_async.call_args
        self.assertEqual(kwargs["args"][0], timer.pk)

    @patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems")
    def test_should_recalc_distances_when_solar_system_has_changed(
        self, mock_calc_distances
    ):
        timer = create_timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        # when
        timer.eve_solar_system = self.system_enaluri
        timer.save()
        # then
        self.assertTrue(mock_calc_distances.called)

    @patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems")
    def test_should_not_recalc_distances_when_solar_system_unchanged(
        self, mock_calc_distances
    ):
        timer = create_timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        # when
        timer.structure_type = self.type_raitaru
        timer.save()
        # then
        self.assertFalse(mock_calc_distances.called)


@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestTimerAccess(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = create_user(cls.character_1)
        cls.user_2 = create_user(cls.character_2)
        cls.user_3 = create_user(cls.character_3)
        cls.user_1 = add_permission_to_user_by_name(
            "structuretimers.create_timer", cls.user_1
        )
        cls.user_2 = add_permission_to_user_by_name(
            "structuretimers.create_timer", cls.user_2
        )
        cls.user_2 = add_permission_to_user_by_name(
            "structuretimers.manage_timer", cls.user_2
        )
        cls.user_2 = add_permission_to_user_by_name(
            "structuretimers.opsec_access", cls.user_2
        )

    def test_creator_can_edit_own_timer(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            user=self.user_1,
        )
        self.assertTrue(timer.user_can_edit(self.user_1))

    def test_manager_can_edit_other_timers(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            user=self.user_1,
        )
        self.assertTrue(timer.user_can_edit(self.user_2))

    def test_non_manager_can_not_edit_other_timer(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            user=self.user_1,
        )
        self.assertFalse(timer.user_can_edit(self.user_3))

    """
    def test_user_with_basic_access_can_view_normal_timer(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            user=self.user_1,
        )
        self.assertTrue(timer.user_can_view(self.user_3))

    def test_user_can_not_view_corp_restricted_timer_from_other_corp(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            eve_corporation=self.corporation_1,
            visibility=Timer.Visibility.CORPORATION,
            user=self.user_1,
        )
        self.assertFalse(timer.user_can_view(self.user_3))

    def test_user_can_view_corp_restricted_timer_from_same_corp(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            eve_corporation=self.corporation_1,
            visibility=Timer.Visibility.CORPORATION,
            user=self.user_1,
        )
        self.assertTrue(timer.user_can_view(self.user_2))

    def test_user_can_not_view_alliance_restricted_timer_from_other_alliance(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            eve_alliance=self.alliance_1,
            visibility=Timer.Visibility.ALLIANCE,
            user=self.user_1,
        )
        self.assertFalse(timer.user_can_view(self.user_3))

    def test_opsec_user_can_view_opsec_timer(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            is_opsec=True,
            user=self.user_2,
        )
        self.assertTrue(timer.user_can_view(self.user_2))

    def test_non_opsec_user_can_not_view_opsec_timer(self):
        timer = Timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            is_opsec=True,
            user=self.user_2,
        )
        self.assertFalse(timer.user_can_view(self.user_1))
    """


@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
@patch("structuretimers.managers.STRUCTURETIMERS_TIMERS_OBSOLETE_AFTER_DAYS", 1)
class TestTimerManger(LoadTestDataMixin, NoSocketsTestCase):
    def test_delete_old_timer(self):
        timer_1 = create_timer(
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now(),
        )
        timer_2 = create_timer(
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now() - dt.timedelta(days=1, seconds=1),
        )
        result = Timer.objects.delete_obsolete()
        self.assertEqual(result, 1)
        self.assertTrue(Timer.objects.filter(pk=timer_1.pk).exists())
        self.assertFalse(Timer.objects.filter(pk=timer_2.pk).exists())

    def test_can_handle_no_timers(self):
        result = Timer.objects.delete_obsolete()
        self.assertEqual(result, 0)


@patch(MODULE_PATH + ".DiscordWebhook.send_message", spec=True)
class TestTimerSendNotification(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )

    @patch(MODULE_PATH + ".STRUCTURETIMER_NOTIFICATION_SET_AVATAR", True)
    def test_should_send_minimal_notification(self, mock_send_message):
        # given
        timer = Timer(
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
        )
        # when
        timer.send_notification(self.webhook)
        # then
        self.assertEqual(mock_send_message.call_count, 1)
        _, kwargs = mock_send_message.call_args
        self.assertEqual(kwargs["username"], __title__)
        self.assertIsNotNone(kwargs["avatar_url"])

    @patch(MODULE_PATH + ".STRUCTURETIMER_NOTIFICATION_SET_AVATAR", False)
    def test_should_send_notification_without_avatar(self, mock_send_message):
        # given
        timer = Timer(
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
        )
        # when
        timer.send_notification(self.webhook)
        # then
        self.assertEqual(mock_send_message.call_count, 1)
        _, kwargs = mock_send_message.call_args
        self.assertIsNone(kwargs["username"])
        self.assertIsNone(kwargs["avatar_url"])

    def test_with_content(self, mock_send_message):
        timer = Timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
        )
        timer.send_notification(self.webhook, "Extra Text")

        self.assertEqual(mock_send_message.call_count, 1)
        _, kwargs = mock_send_message.call_args
        self.assertIn("Extra Text", kwargs["content"])

    def test_timer_with_options_1(self, mock_send_message):
        timer = Timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
            objective=Timer.Objective.FRIENDLY,
        )
        timer.send_notification(self.webhook)

        self.assertEqual(mock_send_message.call_count, 1)

    def test_timer_with_options_2(self, mock_send_message):
        timer = Timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
            objective=Timer.Objective.HOSTILE,
        )
        timer.send_notification(self.webhook)

        self.assertEqual(mock_send_message.call_count, 1)


@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestTimerQuerySet(LoadTestDataMixin, NoSocketsTestCase):
    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.timer_1 = create_timer(
            structure_name="Timer 1",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.ARMOR,
            objective=Timer.Objective.FRIENDLY,
        )
        self.timer_2 = create_timer(
            structure_name="Timer 2",
            date=now() - dt.timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            timer_type=Timer.Type.HULL,
            objective=Timer.Objective.FRIENDLY,
        )
        self.timer_qs = Timer.objects.all()
        self.webhook = DiscordWebhook.objects.create(name="Dummy", url="my-url")

    def test_conforms_with_notification_rule_1(self):
        """
        given two timers in qs
        when one timer conforms with notification rule
        then qs contains only conforming timer
        """
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            require_timer_types=[Timer.Type.ARMOR],
            webhook=self.webhook,
        )
        new_qs = self.timer_qs.conforms_with_notification_rule(rule)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), {self.timer_1.pk})

    def test_conforms_with_notification_rule_2(self):
        """
        given two timers in qs
        when no timer conforms with notification rule
        then qs is empty
        """
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.require_corporations.add(self.corporation_3)
        new_qs = self.timer_qs.conforms_with_notification_rule(rule)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), set())

    def test_conforms_with_notification_rule_3(self):
        """
        given two timers in qs
        when all timer conforms with notification rule
        then qs contains all timers
        """
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            require_objectives=[Timer.Objective.FRIENDLY],
            webhook=self.webhook,
        )
        new_qs = self.timer_qs.conforms_with_notification_rule(rule)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(
            set(new_qs.values_list("pk", flat=True)), {self.timer_1.pk, self.timer_2.pk}
        )


class TestDiscordWebhook(LoadTestDataMixin, TestCase):
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )

    def test_str(self):
        self.assertEqual(str(self.webhook), "Dummy")

    def test_repr(self):
        self.assertEqual(
            repr(self.webhook), f"DiscordWebhook(id={self.webhook.id}, name='Dummy')"
        )

    def test_queue_features(self):
        cache.clear()
        self.assertEqual(self.webhook.queue_size(), 0)
        self.webhook.send_message(content="Dummy message")
        self.assertEqual(self.webhook.queue_size(), 1)
        self.webhook.clear_queue()
        self.assertEqual(self.webhook.queue_size(), 0)

    def test_send_message_normal(self):
        cache.clear()
        embed = dhooks_lite.Embed(description="my_description")
        self.assertEqual(
            self.webhook.send_message(
                content="my_content",
                username="my_username",
                avatar_url="my_avatar_url",
                embeds=[embed],
            ),
            1,
        )
        message = json.loads(
            self.webhook._main_queue.dequeue(), cls=JSONDateTimeDecoder
        )
        expected = {
            "content": "my_content",
            "embeds": [{"description": "my_description", "type": "rich"}],
            "username": "my_username",
            "avatar_url": "my_avatar_url",
        }
        self.assertDictEqual(message, expected)

    def test_send_message_empty(self):
        cache.clear()
        with self.assertRaises(ValueError):
            self.webhook.send_message()


@patch(MODULE_PATH + ".sleep", new=lambda x: x)
@patch(MODULE_PATH + ".DiscordWebhook.send_message_to_webhook", spec=True)
class TestDiscordWebhookSendQueuedMessages(TestCase):
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )
        self.webhook.clear_queue()

    def test_one_message(self, mock_send_message_to_webhook):
        """
        when one mesage in queue
        then send it and returns 1
        """
        mock_send_message_to_webhook.return_value = True
        self.webhook.send_message("dummy")

        result = self.webhook.send_queued_messages()

        self.assertEqual(result, 1)
        self.assertTrue(mock_send_message_to_webhook.called)
        self.assertEqual(self.webhook.queue_size(), 0)

    def test_three_message(self, mock_send_message_to_webhook):
        """
        when three mesages in queue
        then sends them and returns 3
        """
        mock_send_message_to_webhook.return_value = True
        self.webhook.send_message("dummy-1")
        self.webhook.send_message("dummy-2")
        self.webhook.send_message("dummy-3")

        result = self.webhook.send_queued_messages()

        self.assertEqual(result, 3)
        self.assertEqual(mock_send_message_to_webhook.call_count, 3)
        self.assertEqual(self.webhook.queue_size(), 0)

    def test_no_messages(self, mock_send_message_to_webhook):
        """
        when no message in queue
        then do nothing and return 0
        """
        mock_send_message_to_webhook.return_value = True
        result = self.webhook.send_queued_messages()

        self.assertEqual(result, 0)
        self.assertFalse(mock_send_message_to_webhook.called)
        self.assertEqual(self.webhook.queue_size(), 0)

    def test_failed_message(self, mock_send_message_to_webhook):
        """
        given one message in queue
        when sending fails
        then re-queues message and return 0
        """
        mock_send_message_to_webhook.return_value = False
        self.webhook.send_message("dummy")

        result = self.webhook.send_queued_messages()

        self.assertEqual(result, 0)
        self.assertTrue(mock_send_message_to_webhook.called)
        self.assertEqual(self.webhook.queue_size(), 1)


@patch(MODULE_PATH + ".dhooks_lite.Webhook.execute", spec=True)
@patch(MODULE_PATH + ".logger", spec=True)
class TestDiscordWebhookSendMessageToWebhook(NoSocketsTestCase):
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )

    def test_send_normal(self, mock_logger, mock_execute):
        """
        when sending of message successful
        return True
        """
        mock_execute.return_value = dhooks_lite.WebhookResponse(
            headers=dict(), status_code=200
        )
        message = {
            "content": "my_content",
            "embeds": [{"description": "my_description", "type": "rich"}],
            "username": "my_username",
            "avatar_url": "my_avatar_url",
        }

        result = self.webhook.send_message_to_webhook(message)

        self.assertTrue(result)
        self.assertTrue(mock_execute.called)
        _, kwargs = mock_execute.call_args
        self.assertDictEqual(
            kwargs,
            {
                "content": "my_content",
                "embeds": [
                    dhooks_lite.Embed.from_dict(
                        {"description": "my_description", "type": "rich"}
                    )
                ],
                "username": "my_username",
                "avatar_url": "my_avatar_url",
                "wait_for_response": True,
            },
        )
        self.assertFalse(mock_logger.warning.called)

    def test_send_failed(self, mock_logger, mock_execute):
        """
        when sending of message failed
        then log warning and return False
        """
        mock_execute.return_value = dhooks_lite.WebhookResponse(
            headers=dict(), status_code=440
        )
        message = {
            "content": "my_content",
            "embeds": [{"description": "my_description", "type": "rich"}],
            "username": "my_username",
            "avatar_url": "my_avatar_url",
        }

        result = self.webhook.send_message_to_webhook(message)

        self.assertFalse(result)
        self.assertTrue(mock_execute.called)
        self.assertTrue(mock_logger.warning.called)


@patch(MODULE_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleIsMatchingTimer(LoadTestDataMixin, NoSocketsTestCase):
    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(name="Dummy", url="my-url")
        self.timer = create_timer(
            structure_name="Test",
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now(),
        )
        self.rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_15,
            webhook=self.webhook,
        )

    def test_require_timer_types(self):
        # do not process if it does not match
        self.rule.require_timer_types = [Timer.Type.ARMOR]
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.timer_type = Timer.Type.ARMOR
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_timer_types(self):
        # process if it does match
        self.rule.exclude_timer_types = [Timer.Type.ARMOR]
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.timer_type = Timer.Type.ARMOR
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_should_never_match_without_date(self):
        # given
        self.timer.date = None
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_objectives(self):
        # do not process if it does not match
        self.rule.require_objectives = [Timer.Objective.HOSTILE]
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.objective = Timer.Objective.HOSTILE
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_objectives(self):
        # process if it does match
        self.rule.exclude_objectives = [Timer.Objective.HOSTILE]
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.objective = Timer.Objective.HOSTILE
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_corporations(self):
        # do not process if it does not match
        self.rule.require_corporations.add(
            EveCorporationInfo.objects.get(corporation_id=2001)
        )
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.eve_corporation = EveCorporationInfo.objects.get(corporation_id=2001)
        self.timer.save()
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_corporations(self):
        # process if it does match
        self.rule.exclude_corporations.add(
            EveCorporationInfo.objects.get(corporation_id=2001)
        )
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.eve_corporation = EveCorporationInfo.objects.get(corporation_id=2001)
        self.timer.save()
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_alliances(self):
        # do not process if it does not match
        self.rule.require_alliances.add(EveAllianceInfo.objects.get(alliance_id=3001))
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.eve_alliance = EveAllianceInfo.objects.get(alliance_id=3001)
        self.timer.save()
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_alliances(self):
        # process if it does match
        self.rule.exclude_alliances.add(EveAllianceInfo.objects.get(alliance_id=3001))
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.eve_alliance = EveAllianceInfo.objects.get(alliance_id=3001)
        self.timer.save()
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_visibility(self):
        # do not process if it does not match
        self.rule.require_visibility = [Timer.Visibility.CORPORATION]
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.visibility = Timer.Visibility.CORPORATION
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_visibility(self):
        # process if it does match
        self.rule.exclude_visibility = [Timer.Visibility.CORPORATION]
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.visibility = Timer.Visibility.CORPORATION
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_important(self):
        # do not process if it does not match
        self.rule.is_important = NotificationRule.Clause.REQUIRED
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.is_important = True
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_important(self):
        # process if it does match
        self.rule.is_important = NotificationRule.Clause.EXCLUDED
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.is_important = True
        self.assertFalse(self.rule.is_matching_timer(self.timer))

    def test_require_opsec(self):
        # do not process if it does not match
        self.rule.is_opsec = NotificationRule.Clause.REQUIRED
        self.assertFalse(self.rule.is_matching_timer(self.timer))

        # process if it does match
        self.timer.is_opsec = True
        self.assertTrue(self.rule.is_matching_timer(self.timer))

    def test_exclude_opsec(self):
        # process if it does match
        self.rule.is_opsec = NotificationRule.Clause.EXCLUDED
        self.assertTrue(self.rule.is_matching_timer(self.timer))

        # do not process if it does not match
        self.timer.is_opsec = True
        self.assertFalse(self.rule.is_matching_timer(self.timer))


@patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleQuerySet(LoadTestDataMixin, NoSocketsTestCase):
    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(name="Dummy", url="my-url")
        self.rule_1 = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=10,
            require_timer_types=[Timer.Type.ARMOR],
            webhook=self.webhook,
        )
        self.rule_2 = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=15,
            require_objectives=[Timer.Objective.FRIENDLY],
            webhook=self.webhook,
        )
        self.rule_qs = NotificationRule.objects.all()

    def test_conforms_with_timer_1(self):
        """
        given two rules in qs
        when one rule conforms with timer
        then qs contains only conforming rule
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.ARMOR,
            objective=Timer.Objective.HOSTILE,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), {self.rule_1.pk})

    def test_conforms_with_timer_2(self):
        """
        given two rules in qs
        when no rule conforms with timer
        then qs is empty
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.HULL,
            objective=Timer.Objective.HOSTILE,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(set(new_qs.values_list("pk", flat=True)), set())

    def test_conforms_with_timer_3(self):
        """
        given two rules in qs
        when one rule conforms with timer
        then qs contains only conforming rule
        """
        timer = create_timer(
            structure_name="Test Timer",
            date=now() + dt.timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            timer_type=Timer.Type.ARMOR,
            objective=Timer.Objective.FRIENDLY,
        )
        new_qs = self.rule_qs.conforms_with_timer(timer)
        self.assertIsInstance(new_qs, models.QuerySet)
        self.assertSetEqual(
            set(new_qs.values_list("pk", flat=True)), {self.rule_1.pk, self.rule_2.pk}
        )


@patch(MODULE_PATH + ".NotificationRule._import_schedule_notifications_for_rule")
class TestNotificationRuleSave(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(name="dummy", url="dummy-url")

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", True)
    def test_scheduled_normal(self, mock_schedule_notifications):
        """
        given notifications are enabled
        when trigger is scheduled and enabled
        then schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.save()
        self.assertTrue(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def test_scheduled_disabled_1(self, mock_schedule_notifications):
        """
        given notifications are disabled
        when trigger is scheduled and enabled
        then do not schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.save()
        self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", True)
    def test_scheduled_disabled_2(self, mock_schedule_notifications):
        """
        given notifications are enabled
        when trigger is scheduled and disabled
        then do not schedule notifications
        """
        rule = NotificationRule(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
            is_enabled=False,
        )
        rule.save()
        self.assertFalse(mock_schedule_notifications.called)

    @patch(MODULE_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def test_created_trigger(self, mock_schedule_notifications):
        """
        when trigger is created
        then delete all scheduled notifications based on same rule
        """
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        timer = create_timer(
            date=now() + dt.timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        obj = ScheduledNotification.objects.create(
            timer=timer,
            notification_rule=rule,
            timer_date=timer.date,
            notification_date=timer.date - dt.timedelta(minutes=10),
        )
        rule.trigger = NotificationRule.Trigger.NEW_TIMER_CREATED
        rule.scheduled_time = None
        rule.save()

        self.assertFalse(ScheduledNotification.objects.filter(pk=obj.pk).exists())


class TestNotificationRuleMultiselectDisplay(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.choices = [
            (1, "alpha"),
            (2, "bravo"),
        ]

    def test_returns_value_if_found(self):
        self.assertEqual(
            NotificationRule.get_multiselect_display(1, self.choices), "alpha"
        )
        self.assertEqual(
            NotificationRule.get_multiselect_display(2, self.choices), "bravo"
        )

    def test_raises_exception_if_not_found(self):
        with self.assertRaises(ValueError):
            NotificationRule.get_multiselect_display(3, self.choices)


@patch("structuretimers.tasks.retry_task_if_esi_is_down", lambda self: None)
@patch(MODULE_PATH + ".EveSolarSystem.distance_to", lambda *args, **kwargs: 4.257e16)
@patch(MODULE_PATH + ".EveSolarSystem.jumps_to", lambda *args, **kwargs: 3)
@patch(MODULE_PATH + "._task_calc_staging_system", wraps=_task_calc_staging_system)
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestStagingSystem(LoadTestDataMixin, NoSocketsTestCase):
    def test_should_calc_distances(self, spy_task_calc_staging_system):
        # given
        timer = create_timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        # when
        staging_system = StagingSystem.objects.create(
            eve_solar_system=self.system_enaluri
        )
        # then
        obj = timer.distances.first()
        self.assertEqual(obj.staging_system, staging_system)
        self.assertAlmostEqual(obj.light_years, 4.5, delta=0.1)
        self.assertEqual(obj.jumps, 3)
        self.assertTrue(spy_task_calc_staging_system.called)

    def test_should_not_update_distances_when_solar_system_not_changed(
        self, spy_task_calc_staging_system
    ):
        # given
        create_timer(
            structure_name="Test",
            timer_type=Timer.Type.ARMOR,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=dt.datetime(2020, 8, 6, 13, 25, tzinfo=utc),
        )
        staging_system = create_staging_system(eve_solar_system=self.system_enaluri)
        # when
        staging_system.save()
        # then
        self.assertFalse(spy_task_calc_staging_system.called)
