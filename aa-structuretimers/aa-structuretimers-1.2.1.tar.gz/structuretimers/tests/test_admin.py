from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django_webtest import WebTest

from ..models import DiscordWebhook, NotificationRule, StagingSystem, Timer
from .testdata.factory import create_staging_system
from .testdata.fixtures import LoadTestDataMixin


@patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleChangeList(LoadTestDataMixin, WebTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )
        cls.user = User.objects.create_superuser(
            "Bruce Wayne", "bruce@example.com", "password"
        )

    @patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            require_timer_types=[Timer.Type.ARMOR],
            webhook=self.webhook,
        )
        rule = NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            webhook=self.webhook,
        )
        rule.require_corporations.add(self.corporation_1)
        NotificationRule.objects.create(
            trigger=NotificationRule.Trigger.SCHEDULED_TIME_REACHED,
            scheduled_time=NotificationRule.MINUTES_10,
            is_important=NotificationRule.Clause.EXCLUDED,
            webhook=self.webhook,
        )

    def test_can_open_page_normally(self):
        # login
        self.app.set_user(self.user)

        # user tries to add new notification rule
        add_page = self.app.get(
            reverse("admin:structuretimers_notificationrule_changelist")
        )
        self.assertEqual(add_page.status_code, 200)


@patch("structuretimers.models.STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestNotificationRuleValidations(LoadTestDataMixin, WebTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webhook = DiscordWebhook.objects.create(
            name="Dummy", url="http://www.example.com"
        )
        cls.user = User.objects.create_superuser(
            "Bruce Wayne", "bruce@example.com", "password"
        )
        cls.url_add = reverse("admin:structuretimers_notificationrule_add")
        cls.url_changelist = reverse(
            "admin:structuretimers_notificationrule_changelist"
        )

    def _open_page(self) -> object:
        # login
        self.app.set_user(self.user)

        # user tries to add new notification rule
        add_page = self.app.get(self.url_add)
        self.assertEqual(add_page.status_code, 200)
        form = add_page.form
        form["trigger"] = NotificationRule.Trigger.SCHEDULED_TIME_REACHED
        form["scheduled_time"] = NotificationRule.MINUTES_10
        form["webhook"] = self.webhook.pk
        return form

    def test_no_errors(self):
        form = self._open_page()
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url_changelist)
        self.assertEqual(NotificationRule.objects.count(), 1)

    def test_can_not_have_same_options_timer_types(self):
        form = self._open_page()
        form["require_timer_types"] = [Timer.Type.ANCHORING, Timer.Type.HULL]
        form["exclude_timer_types"] = [Timer.Type.ANCHORING, Timer.Type.ARMOR]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_objectives(self):
        form = self._open_page()
        form["require_objectives"] = [Timer.Objective.FRIENDLY, Timer.Objective.HOSTILE]
        form["exclude_objectives"] = [Timer.Objective.FRIENDLY, Timer.Objective.NEUTRAL]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_visibility(self):
        form = self._open_page()
        form["require_visibility"] = [Timer.Visibility.CORPORATION]
        form["exclude_visibility"] = [Timer.Visibility.CORPORATION]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_corporations(self):
        form = self._open_page()
        form["require_corporations"] = [self.corporation_1.pk, self.corporation_3.pk]
        form["exclude_corporations"] = [self.corporation_1.pk]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)

    def test_can_not_have_same_options_alliances(self):
        form = self._open_page()
        form["require_alliances"] = [self.alliance_1.pk, self.alliance_3.pk]
        form["exclude_alliances"] = [self.alliance_1.pk]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please correct the error below", response.text)
        self.assertEqual(NotificationRule.objects.count(), 0)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestStagingSystemAdmin(LoadTestDataMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser("Bruce Wayne")
        cls.url_add = reverse("admin:structuretimers_stagingsystem_add")

    def test_should_create_new_staging_system(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.post(
            self.url_add, data={"eve_solar_system": self.system_abune.pk}
        )
        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(StagingSystem.objects.count(), 1)
        obj = StagingSystem.objects.first()
        self.assertEqual(obj.eve_solar_system, self.system_abune)
        self.assertFalse(obj.is_main)

    def test_should_ensure_only_one_obj_is_main(self):
        # given
        self.client.force_login(self.user)
        create_staging_system(eve_solar_system=self.system_enaluri, is_main=True)
        # when
        res = self.client.post(
            self.url_add,
            data={"eve_solar_system": self.system_abune.pk, "is_main": True},
        )
        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            StagingSystem.objects.filter(is_main=True).get().eve_solar_system,
            self.system_abune,
        )
