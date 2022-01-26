from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from .app_settings import STRUCTURETIMERS_TIMERS_OBSOLETE_AFTER_DAYS


class NotificationRuleQuerySet(models.QuerySet):
    def conforms_with_timer(self, timer: object) -> models.QuerySet:
        """Return new queryset based on current queryset,
        which only contains notification rules that conforms with the given timer.
        """
        matching_rule_pks = list()
        for notification_rule in self:
            if notification_rule.is_matching_timer(timer):
                matching_rule_pks.append(notification_rule.pk)

        return self.filter(pk__in=matching_rule_pks)


class NotificationRuleManagerBase(models.Manager):
    pass


NotificationRuleManager = NotificationRuleManagerBase.from_queryset(
    NotificationRuleQuerySet
)


class TimerQuerySet(models.QuerySet):
    def conforms_with_notification_rule(
        self, notification_rule: object
    ) -> models.QuerySet:
        """Return new queryset based on current queryset,
        which only contains timers that conform with the given notification rule.
        """
        matching_timer_pks = list()
        for timer in self:
            if notification_rule.is_matching_timer(timer):
                matching_timer_pks.append(timer.pk)
        return self.filter(pk__in=matching_timer_pks)

    def visible_to_user(self, user: User) -> models.QuerySet:
        """returns updated queryset of all timers visible to the given user"""
        user_characters_qs = user.character_ownerships.select_related(
            "character_ownerships__character"
        ).values("character__corporation_id", "character__alliance_id")
        user_corporation_ids = {
            x["character__corporation_id"] for x in user_characters_qs
        }
        user_alliance_ids = {x["character__alliance_id"] for x in user_characters_qs}
        timers_qs = self.select_related(
            "structure_type", "eve_corporation", "eve_alliance"
        )
        if not user.has_perm("structuretimers.opsec_access"):
            timers_qs = timers_qs.exclude(is_opsec=True)

        timers_qs = (
            timers_qs.filter(visibility=self.model.Visibility.UNRESTRICTED)
            | timers_qs.filter(user=user)
            | timers_qs.filter(
                visibility=self.model.Visibility.CORPORATION,
                eve_corporation__corporation_id__in=user_corporation_ids,
            )
            | timers_qs.filter(
                visibility=self.model.Visibility.ALLIANCE,
                eve_alliance__alliance_id__in=user_alliance_ids,
            )
        )
        return timers_qs

    def filter_by_tab(self, tab_name: str, max_hours_passed: int) -> models.QuerySet:
        """Filter timers for tabs."""
        if tab_name == "current":
            return self.filter(date__gte=now() - timedelta(hours=max_hours_passed))
        elif tab_name == "preliminary":
            return self.filter(timer_type=self.model.Type.PRELIMINARY)
        elif tab_name == "past":
            return self.filter(date__lt=now())
        raise ValueError(f"Invalid tab name: {tab_name}")


class TimerManagerBase(models.Manager):
    def delete_obsolete(self) -> int:
        """delete all timers that are considered obsolete"""
        if STRUCTURETIMERS_TIMERS_OBSOLETE_AFTER_DAYS:
            deadline = now() - timedelta(
                days=STRUCTURETIMERS_TIMERS_OBSOLETE_AFTER_DAYS
            )
            _, details = self.filter(date__lt=deadline).delete()
            key = f"{self.model._meta.app_label}.{self.model.__name__}"
            if key in details:
                deleted_count = details[key]
                return deleted_count
        return 0


TimerManager = TimerManagerBase.from_queryset(TimerQuerySet)


class DistancesFromStagingManager(models.Manager):
    def calc_timer_for_staging_system(
        self,
        timer: models.Model,
        staging_system: models.Model,
        force_update: bool = False,
    ):
        """Calculate distances for a timer from a staging system."""
        obj, created = self.get_or_create(timer=timer, staging_system=staging_system)
        if force_update or created:
            obj.calculate()
            obj.save()
