from datetime import timedelta
from unittest.mock import Mock, patch

from celery import Task

from django.test import TestCase, TransactionTestCase
from django.utils.timezone import now
from eveuniverse.models import EveSolarSystem, EveType

from ..models import DiscordWebhook, NotificationRule, ScheduledNotification, Timer
from ..tasks import (
    notify_about_new_timer,
    schedule_notifications_for_rule,
    schedule_notifications_for_timer,
    send_messages_for_webhook,
    send_scheduled_notification,
)
from .testdata.factory import create_timer
from .testdata.fixtures import LoadTestDataMixin
from .testdata.load_eveuniverse import load_eveuniverse

MODULE_PATH = "structuretimers.tasks"


class TestCaseBase(LoadTestDataMixin, TestCase):
    @patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )
        self.webhook.clear_queue()
        self.rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_15,
            webhook=self.webhook,
        )
        self.timer = create_timer(
            structure_name="Test_1",
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now() + timedelta(minutes=30),
        )


@patch(MODULE_PATH + ".DiscordWebhook.send_queued_messages", spec=True)
@patch(MODULE_PATH + ".logger", spec=True)
class TestSendMessagesForWebhook(TestCaseBase):
    def test_normal(self, mock_logger, mock_send_queued_messages):
        send_messages_for_webhook(self.webhook.pk)
        self.assertEqual(mock_send_queued_messages.call_count, 1)
        self.assertEqual(mock_logger.info.call_count, 2)
        self.assertEqual(mock_logger.error.call_count, 0)

    def test_disabled_webhook(self, mock_logger, mock_send_queued_messages):
        self.webhook.is_enabled = False
        self.webhook.save()

        send_messages_for_webhook(self.webhook.pk)
        self.assertEqual(mock_send_queued_messages.call_count, 0)
        self.assertEqual(mock_logger.info.call_count, 1)
        self.assertEqual(mock_logger.error.call_count, 0)


@patch(MODULE_PATH + ".notify_about_new_timer", spec=True)
@patch(MODULE_PATH + ".send_scheduled_notification", spec=True)
class TestScheduleNotificationForTimer(TestCaseBase):
    def test_normal(self, mock_send_notification, mock_send_notification_for_timer):
        """
        given no notifications scheduled
        when called for timer with matching notification rule
        then schedules new notification
        """
        mock_send_notification.apply_async.return_value.task_id = "my_task_id"

        schedule_notifications_for_timer(timer_pk=self.timer.pk, is_new=True)

        self.assertTrue(mock_send_notification.apply_async.called)
        self.assertTrue(
            self.timer.scheduled_notifications.filter(notification_rule=self.rule)
        )

    def test_should_not_create_notification_for_preliminary_timer(
        self, mock_send_notification, mock_send_notification_for_timer
    ):
        # given
        mock_send_notification.apply_async.return_value.task_id = "my_task_id"
        timer = create_timer(timer_type=Timer.Type.PRELIMINARY)
        # when/then
        with self.assertRaises(ValueError):
            schedule_notifications_for_timer(timer_pk=timer.pk, is_new=True)

    def test_remove_old_notifications(
        self, mock_send_notification, mock_send_notification_for_timer
    ):
        """
        given existing notification
        when called for timer with matching notification rule and changed date
        then deletes existing notification and schedules new notification
        """
        mock_send_notification.apply_async.return_value.task_id = "my_task_id"
        notification_old = ScheduledNotification.objects.create(
            timer=self.timer,
            notification_rule=self.rule,
            timer_date=self.timer.date + timedelta(minutes=5),
            notification_date=self.timer.date - timedelta(minutes=5),
            celery_task_id="99",
        )

        schedule_notifications_for_timer(timer_pk=self.timer.pk, is_new=True)

        self.assertTrue(mock_send_notification.apply_async.called)
        self.assertTrue(
            self.timer.scheduled_notifications.filter(
                notification_rule=self.rule
            ).exists()
        )
        self.assertFalse(
            ScheduledNotification.objects.filter(pk=notification_old.pk).exists()
        )

    def test_notification_for_new_timer(
        self, mock_send_notification, mock_send_notification_for_timer
    ):
        """
        given notification rule for sending new timers exists
        when called for timer
        then send new notification
        """
        self.rule.is_enabled = False
        self.rule.save()
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.NEW_TIMER_CREATED, webhook=self.webhook
        )
        schedule_notifications_for_timer(timer_pk=self.timer.pk, is_new=True)

        self.assertTrue(mock_send_notification_for_timer.apply_async.called)
        _, kwargs = mock_send_notification_for_timer.apply_async.call_args
        self.assertEqual(kwargs["kwargs"]["timer_pk"], self.timer.pk)
        self.assertEqual(kwargs["kwargs"]["notification_rule_pk"], rule.pk)

    def test_no_notification_for_new_timer_if_no_rule(
        self, mock_send_notification, mock_send_notification_for_timer
    ):
        """
        given no notification rule for sending new timers exists
        when called for timer
        then no notification is sent
        """
        self.rule.is_enabled = False
        self.rule.save()
        schedule_notifications_for_timer(timer_pk=self.timer.pk, is_new=True)

        self.assertFalse(mock_send_notification_for_timer.apply_async.called)


@patch(MODULE_PATH + ".send_scheduled_notification", spec=True)
class TestScheduleNotificationForRule(TestCaseBase):
    def test_normal(self, mock_send_notification):
        """
        given no notifications scheduled
        when called for notification rule with matching timer
        then schedules new notification
        """
        mock_send_notification.apply_async.return_value.task_id = "my_task_id"

        schedule_notifications_for_rule(self.rule.pk)

        self.assertTrue(mock_send_notification.apply_async.called)
        self.assertTrue(
            self.timer.scheduled_notifications.filter(
                notification_rule=self.rule
            ).exists()
        )

    def test_remove_old_notifications(self, mock_send_notification):
        """
        given existing notification
        when called for notification rule with matching timer
        then deletes existing notification and schedules new notification
        """
        mock_send_notification.apply_async.return_value.task_id = "my_task_id"
        notification_old = ScheduledNotification.objects.create(
            timer=self.timer,
            notification_rule=self.rule,
            timer_date=self.timer.date + timedelta(minutes=5),
            notification_date=self.timer.date - timedelta(minutes=5),
            celery_task_id="99",
        )

        schedule_notifications_for_rule(self.rule.pk)

        self.assertTrue(mock_send_notification.apply_async.called)
        self.assertTrue(
            self.timer.scheduled_notifications.filter(
                notification_rule=self.rule
            ).exists()
        )
        self.assertFalse(
            ScheduledNotification.objects.filter(pk=notification_old.pk).exists()
        )


@patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
@patch(MODULE_PATH + ".send_messages_for_webhook", spec=True)
class TestSendScheduledNotification(TransactionTestCase):
    @patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        load_eveuniverse()
        self.type_raitaru = EveType.objects.get(id=35825)
        self.system_abune = EveSolarSystem.objects.get(id=30004984)
        self.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )
        self.webhook.clear_queue()
        self.rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_15,
            webhook=self.webhook,
        )
        self.timer = create_timer(
            structure_name="Test_1",
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now() + timedelta(minutes=30),
        )
        ScheduledNotification.objects.all().delete()

    def test_normal(self, mock_send_messages_for_webhook):
        """
        when this notification is correctly scheduled
        then send the notification
        """
        scheduled_notification = ScheduledNotification.objects.create(
            timer=self.timer,
            notification_rule=self.rule,
            celery_task_id="my-id-123",
            timer_date=now() + timedelta(hours=1),
            notification_date=now() + timedelta(minutes=30),
        )
        mock_task = Mock(spec=Task)
        mock_task.request.id = "my-id-123"
        send_scheduled_notification_inner = (
            send_scheduled_notification.__wrapped__.__func__
        )
        send_scheduled_notification_inner(
            mock_task, scheduled_notification_pk=scheduled_notification.pk
        )
        self.assertTrue(mock_send_messages_for_webhook.apply_async.called)

    def test_revoked_notification(self, mock_send_messages_for_webhook):
        """
        when this is not the right task instance
        then discard this notification
        """
        scheduled_notification = ScheduledNotification.objects.create(
            timer=self.timer,
            notification_rule=self.rule,
            celery_task_id="my-id-123",
            timer_date=now() + timedelta(hours=1),
            notification_date=now() + timedelta(minutes=30),
        )
        mock_task = Mock(**{"request.id": "my-id-456"})
        send_scheduled_notification_inner = (
            send_scheduled_notification.__wrapped__.__func__
        )
        send_scheduled_notification_inner(
            mock_task, scheduled_notification_pk=scheduled_notification.pk
        )
        self.assertFalse(mock_send_messages_for_webhook.apply_async.called)

    def test_rule_disabled(self, mock_send_messages_for_webhook):
        """
        when the notification rule for this scheduled notification is disabled
        then discard notification
        """
        self.rule.is_enabled = False
        self.rule.save()
        scheduled_notification = ScheduledNotification.objects.create(
            timer=self.timer,
            notification_rule=self.rule,
            celery_task_id="my-id-123",
            timer_date=now() + timedelta(hours=1),
            notification_date=now() + timedelta(minutes=30),
        )
        mock_task = Mock(spec=Task)
        mock_task.request.id = "my-id-123"
        send_scheduled_notification_inner = (
            send_scheduled_notification.__wrapped__.__func__
        )
        send_scheduled_notification_inner(
            mock_task, scheduled_notification_pk=scheduled_notification.pk
        )
        self.assertFalse(mock_send_messages_for_webhook.apply_async.called)


@patch(MODULE_PATH + ".send_messages_for_webhook", spec=True)
class TestSendNotificationForTimer(TestCaseBase):
    def setUp(self) -> None:
        super().setUp()
        self.rule_2 = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.NEW_TIMER_CREATED, webhook=self.webhook
        )

    def test_normal(self, mock_send_messages_for_webhook):
        """
        given rule for notifying about new timers exist
        when calling task for a timer
        then send notification for that timer
        """
        notify_about_new_timer(self.timer.pk, self.rule_2.pk)

        self.assertTrue(mock_send_messages_for_webhook.apply_async.called)
        _, kwargs = mock_send_messages_for_webhook.apply_async.call_args
        self.assertListEqual(kwargs["args"], [self.webhook.pk])

    def test_webhook_disabled(self, mock_send_messages_for_webhook):
        """
        given rule for notifying about new timers does NOT exist
        when calling task for a timer
        then send notification for that timer
        """
        notify_about_new_timer(self.timer.pk, self.rule_2.pk)

        self.assertTrue(mock_send_messages_for_webhook.apply_async.called)
        _, kwargs = mock_send_messages_for_webhook.apply_async.call_args
        self.assertListEqual(kwargs["args"], [self.webhook.pk])
