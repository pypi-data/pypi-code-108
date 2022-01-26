import datetime as dt
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.utils.timezone import now

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils
from app_utils.helpers import random_string

from ...models import (
    DiscordWebhook,
    DistancesFromStaging,
    NotificationRule,
    ScheduledNotification,
    StagingSystem,
    Timer,
)


def add_main_to_user(user: User, character: EveCharacter):
    CharacterOwnership.objects.create(
        user=user, owner_hash="x1" + character.character_name, character=character
    )
    user.profile.main_character = character
    user.profile.save()


def create_user(character: EveCharacter) -> User:
    User.objects.filter(username=character.character_name).delete()
    user = AuthUtils.create_user(character.character_name)
    add_main_to_user(user, character)
    AuthUtils.add_permission_to_user_by_name("structuretimers.basic_access", user)
    user = User.objects.get(pk=user.pk)
    return user


def create_timer(*args, **kwargs):
    with patch(
        "structuretimers.models._task_calc_timer_distances_for_all_staging_systems",
        Mock(),
    ):
        if "light_years" in kwargs:
            light_years = kwargs.pop("light_years")
        else:
            light_years = None
        if "jumps" in kwargs:
            jumps = kwargs.pop("jumps")
        else:
            jumps = None
        if "eve_solar_system" not in kwargs and "eve_solar_system_id" not in kwargs:
            kwargs["eve_solar_system_id"] = 30004984
        if "structure_type" not in kwargs and "structure_type_id" not in kwargs:
            kwargs["structure_type_id"] = 35825
        if "enabled_notifications" in kwargs:
            kwargs.pop("enabled_notifications")
            timer = Timer.objects.create(*args, **kwargs)
        else:
            with patch(
                "structuretimers.models._task_schedule_notifications_for_timer", Mock()
            ):
                timer = Timer.objects.create(*args, **kwargs)
        if light_years or jumps:
            for staging_system in StagingSystem.objects.all():
                DistancesFromStaging.objects.update_or_create(
                    staging_system=staging_system,
                    timer=timer,
                    defaults={"light_years": light_years, "jumps": jumps},
                )
        return timer


def create_staging_system(*args, **kwargs):
    if "light_years" in kwargs:
        light_years = kwargs.pop("light_years")
    else:
        light_years = None
    if "jumps" in kwargs:
        jumps = kwargs.pop("jumps")
    else:
        jumps = None
    with patch("structuretimers.models._task_calc_staging_system", Mock()):
        staging_system = StagingSystem.objects.create(*args, **kwargs)
        if light_years or jumps:
            for timer in Timer.objects.all():
                DistancesFromStaging.objects.update_or_create(
                    staging_system=staging_system,
                    timer=timer,
                    defaults={"light_years": light_years, "jumps": jumps},
                )
        return staging_system


def create_discord_webhook(*args, **kwargs):
    if "name" not in kwargs:
        while True:
            name = f"dummy{random_string(8)}"
            if not DiscordWebhook.objects.filter(name=name).exists():
                break
        kwargs["name"] = name
    if "url" not in kwargs:
        kwargs["url"] = f"https://www.example.com/{kwargs['name']}"
    return DiscordWebhook.objects.create(*args, **kwargs)


def create_notification_rule(*args, **kwargs):
    if "webhook" not in kwargs:
        kwargs["webhook"] = create_discord_webhook()
    if "trigger" not in kwargs:
        kwargs["trigger"] = NotificationRule.Trigger.SCHEDULED_TIME_REACHED
    if "scheduled_time" not in kwargs:
        kwargs["scheduled_time"] = 60
    return NotificationRule.objects.create(*args, **kwargs)


def create_scheduled_notification(*args, **kwargs):
    if "timer_date" not in kwargs:
        kwargs["timer_date"] = now() + dt.timedelta(hours=1)
    if "notification_date" not in kwargs:
        kwargs["notification_date"] = now() + dt.timedelta(minutes=45)
    if "celery_task_id" not in kwargs:
        kwargs["celery_task_id"] = random_string(8)
    return ScheduledNotification.objects.create(*args, **kwargs)
