#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
import os
import uuid

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django_auto_one_to_one import AutoOneToOneModel
from model_utils import Choices
from model_utils.fields import SplitField
from model_utils.models import TimeStampedModel
from nobinobi_child.models import Child, Classroom, Period
from nobinobi_staff.models import Staff
from notifications.models import Notification

from nobinobi_daily_follow_up.utils import range_time


class Presence(TimeStampedModel):
    """
    Models for Presence
    """
    child = models.ForeignKey(
        to=Child,
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    date = models.DateField(_("Date"))
    arrival_time = models.TimeField(_("Arrival time"))
    departure_time = models.TimeField(_("Departure time"), blank=True, null=True)
    intermediate_departure_time = models.TimeField(_("Intermediate departure time"), blank=True, null=True)
    intermediate_arrival_time = models.TimeField(_("Intermediate arrival time"), blank=True, null=True)

    classroom = models.ForeignKey(
        to=Classroom,
        verbose_name=_("Classroom"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )

    class Meta:
        unique_together = ("child", "date")
        ordering = ('date',)
        verbose_name = _('Presence')
        verbose_name_plural = _('Presences')

    def __str__(self):
        return _("Presence: {} - {} - {}").format(self.child.full_name, self.date,
                                                  self.classroom.name if self.classroom else "-")

    def save(self, *args, **kwargs):
        super(Presence, self).save(*args, **kwargs)
        self.dailyfollowup.save()


class DailyFollowUp(AutoOneToOneModel(Presence, attr="presence"), TimeStampedModel):
    """
    Model for DailyFollowUp
    """
    important = models.BooleanField(_("Important"), default=False)
    comment = models.TextField(_("Comment"), blank=True, null=True)

    lotions = models.ManyToManyField(
        to="Lotion",
        verbose_name=_("Lotions"),
        through="LotionDailyFollowUp",
        through_fields=("daily_follow_up", "lotion")
    )
    medications = models.ManyToManyField(
        to="Medication",
        verbose_name=_("Medications"),
        through="DailyFollowUpToMedication",
        through_fields=("daily_follow_up", "medication")
    )
    activities = models.ManyToManyField(
        to="TypeActivity",
        verbose_name=_("Activities"),
        through="Activity",
        through_fields=("daily_follow_up", "type_activity")
    )

    class Meta:
        ordering = ("presence",)
        verbose_name = _("Daily follow-up")
        verbose_name_plural = _("Daily follow-ups")

    def __str__(self):
        return _("Daily follow-up: {} - {}").format(self.presence.date, self.presence.child.full_name)


class Activity(TimeStampedModel):
    """
    Model for Activity
    """
    daily_follow_up = models.ForeignKey(
        to="DailyFollowUp",
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    type_activity = models.ForeignKey(
        to="TypeActivity",
        verbose_name=_("Type activity"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    comment = SplitField(_("Comment"), blank=True, null=True)

    class Meta:
        ordering = ('daily_follow_up', 'type_activity',)
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')

    def __str__(self):
        return _("Activity: {} - {} - {}").format(self.daily_follow_up, self.type_activity.name,
                                                  self.type_activity.group.name)


class TypeActivity(TimeStampedModel):
    """
    Model for TypeActivity
    """
    name = models.CharField(_("Name"), max_length=50)
    group = models.ForeignKey(
        to="ActivityGroup",
        verbose_name=_("Group"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    order = models.PositiveSmallIntegerField(_("Order"))

    class Meta:
        ordering = ('order', 'name', 'group',)
        verbose_name = _('Type activity')
        verbose_name_plural = _('Types activities')

    def __str__(self):
        return "{} ({})".format(self.name, self.group.name)


class ActivityGroup(TimeStampedModel):
    """
    Model for ActivityGroup
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Activity group')
        verbose_name_plural = _('Activities groups')

    def __str__(self):
        return self.name


class Nap(TimeStampedModel):
    """
    Model for Nap
    """
    daily_follow_up = models.ForeignKey(
        to="DailyFollowUp",
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    start_time = models.TimeField(_("Start time"))
    end_time = models.TimeField(_("End time"), blank=True, null=True)

    class Meta:
        ordering = ('start_time', 'end_time',)
        verbose_name = _('Nap')
        verbose_name_plural = _('Naps')

    def __str__(self):
        return _("Nap: {} - {} - {}").format(self.daily_follow_up, self.start_time, self.end_time)


class LotionDailyFollowUp(TimeStampedModel):
    """
    Model for LotionDailyFollowUp
    """
    daily_follow_up = models.ForeignKey(
        to="DailyFollowUp",
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    lotion = models.ForeignKey(
        to="Lotion",
        verbose_name=_("Lotion"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    comment = SplitField(_("Comment"), blank=True, null=True)

    class Meta:
        ordering = ("daily_follow_up",)
        verbose_name = _("Lotion daily follow-up")
        verbose_name_plural = _("Lotion daily follow-ups")

    def __str__(self):
        return "Lotion: {} - {}".format(self.daily_follow_up, self.lotion.name)


class Lotion(TimeStampedModel):
    """
    Model for Lotion
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Lotion')
        verbose_name_plural = _('Lotions')

    def __str__(self):
        return self.name


class DiaperChange(TimeStampedModel):
    """
    Model for DiaperChange
    """
    FECES_CHOICES = Choices(
        ("feces", "caca.png"),
        ("nothing", "nothing.png"),
    )

    daily_follow_up = models.ForeignKey(
        to="DailyFollowUp",
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    hour = models.TimeField(_("Hour"))
    feces = models.CharField(_("Feces"), choices=FECES_CHOICES, default=FECES_CHOICES.nothing, max_length=15)

    class Meta:
        ordering = ('daily_follow_up', 'hour',)
        verbose_name = _('Diaper change')
        verbose_name_plural = _('Diapers changes')

    def __str__(self):
        return _("Diaper change: {} - {} - {}").format(self.daily_follow_up, self.hour, self.feces)


class DailyFollowUpToMedication(models.Model):
    """"""
    daily_follow_up = models.ForeignKey(
        to="DailyFollowUp",
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
    )
    medication = models.ForeignKey(
        to="Medication",
        verbose_name=_("Medication"),
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('daily_follow_up', 'medication',)
        verbose_name = _('Daily Follow-up to Medication')
        # verbose_name_plural = _('')

    def __str__(self):
        return "{} - {}".format(self.daily_follow_up, self.medication)


class Medication(TimeStampedModel):
    """
    Model for
    """

    def attachment_file_medication(self, filename):
        f, ext = os.path.splitext(filename)
        upload_to = "docs/medication/{}/".format(self.child.slug)
        return '%s%s%s' % (upload_to, uuid.uuid4().hex, ext)

    type_medication = models.ForeignKey(
        to="TypeMedication",
        verbose_name=_("Type medication"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    from_date = models.DateField(_("From date"))
    end_date = models.DateField(_("End date"))
    child = models.ForeignKey(
        to=Child,
        verbose_name=_("Child"),
        on_delete=models.CASCADE
    )
    comment = SplitField(_("Comment"), blank=True, null=True)
    attachment = models.FileField(_("Attachment"), upload_to=attachment_file_medication, blank=True, null=True)

    class Meta:
        ordering = ("from_date", 'end_date', "type_medication")
        verbose_name = _("Medication")
        verbose_name_plural = _("Medications")

    def __str__(self):
        return _("Medication: {} - {} | {}").format(self.from_date, self.end_date, self.type_medication.name)


class TypeMedication(TimeStampedModel):
    """
    Model for TypeMedication
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Type medication')
        verbose_name_plural = _('Types medications')

    def __str__(self):
        return self.name


class Reception(AutoOneToOneModel(DailyFollowUp, attr="daily_follow_up"), TimeStampedModel):
    """
    Model for Reception
    """
    SLEEP_CHOICES = Choices(
        ('very_good', 'miao.png'),
        ("good", "smile.png"),
        ("bad", "spook.png"),
    )
    BREAKFAST_CHOICES = Choices(
        ('very_good', 'miao.png'),
        ('good', 'smile.png'),
        ('nothing', 'nothing.png')
    )
    CONDITION_CHOICES = Choices(
        ("very_good", "miao.png"),
        ("good", "smile.png"),
        ("sick", "spook.png")
    )

    FEVER_CHOICES = Choices(
        ("no", _("No")),
        ("37", "37"),
        ("37.5", "37.5"),
        ("38", "38"),
        ("38.5", "38.5"),
        ("39", "39"),
        ("39.5", "39.5"),
        ("40", "40")
    )

    SICK_CHOICES = Choices(
        ("no", _("No")),
        ("gastroenteritis", _("Gastroenteritis")),
        ("conjunctivitis", _("Conjunctivitis")),
        ("cough", _("Cough")),
        ("cold", _("Cold"))
    )

    wake_up_time = models.TimeField(verbose_name=_("Wake up time"), choices=range_time(3, 15, 5, 00), null=True,
                                    blank=True)
    sleep = models.CharField(choices=SLEEP_CHOICES, verbose_name=_("Sleep"), max_length=10, null=True,
                             blank=False, default=SLEEP_CHOICES.very_good)
    breakfast = models.CharField(choices=BREAKFAST_CHOICES, verbose_name=_("Breakfast"), max_length=20,
                                 null=True, blank=False, default=BREAKFAST_CHOICES.very_good)
    breakfast_time = models.TimeField(verbose_name=_("Breakfast time"), null=True, blank=True, )

    condition = models.CharField(verbose_name=_("Condition"), choices=CONDITION_CHOICES, max_length=10, null=True,
                                 blank=False, default=CONDITION_CHOICES.very_good)
    fever = models.CharField(verbose_name=_("Fever"), choices=FEVER_CHOICES, max_length=10, null=True, blank=False,
                             default=FEVER_CHOICES.no)
    sick = models.CharField(verbose_name=_("Sick"), choices=SICK_CHOICES, max_length=25, null=True, blank=False,
                            default=SICK_CHOICES.no)

    comment = models.TextField(verbose_name=_("Comment"), null=True, blank=True)

    class Meta:
        ordering = ('daily_follow_up',)
        verbose_name = _('Reception')
        verbose_name_plural = _('Receptions')

    def __str__(self):
        return _("Reception: {}").format(self.daily_follow_up)


class GiveMedication(TimeStampedModel):
    """
    Model for GiveMedication
    """
    medication = models.ForeignKey(
        to="Medication",
        verbose_name=_("Medication"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    staff = models.ForeignKey(
        to=Staff,
        verbose_name=_("Staff"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    date = models.DateField(_("Date"))
    give_hour = models.TimeField(_("Give hour"), blank=False, null=False)
    given_hour = models.TimeField(_("Given hour"), blank=True, null=True)

    class Meta:
        ordering = ("medication",)
        verbose_name = _("Give medication")
        verbose_name_plural = _("Give medications")

    def __str__(self):
        give_hour = self.give_hour if self.give_hour else ""
        medication = self.medication if self.medication else ""
        staff = self.staff.full_name if self.staff is not None else ""
        return _("Give medication: {} - {} - {}").format(give_hour, medication, staff)


class MealDailyFollowUp(AutoOneToOneModel(DailyFollowUp, attr="daily_follow_up"), TimeStampedModel):
    """
    Model for MealDailyFollowUp
    """
    MEAL_QUALITY_CHOICES = Choices(
        ("", "question.png"),
        ("very_good", "miao.png"),
        ("good", "smile.png"),
        ("nothing", "nothing.png"),
    )

    snack_meals = models.ManyToManyField(
        to="Meal",
        verbose_name=_("Snack meals"),
        related_name="snack_meals",
        blank=True,
    )
    snack_time = models.TimeField(_("Snack time"), blank=True, null=True)
    snack_quality = models.CharField(_("Snack quality"), choices=MEAL_QUALITY_CHOICES, max_length=10, blank=True,
                                     null=True)
    lunch_meals = models.ManyToManyField(
        to="Meal",
        verbose_name=_("Lunch meals"),
        related_name="lunch_meals",
        blank=True,
    )
    lunch_time = models.TimeField(_("Lunch time"), blank=True, null=True)
    lunch_quality = models.CharField(_("Lunch quality"), choices=MEAL_QUALITY_CHOICES, max_length=10, blank=True,
                                     null=True)
    afternoon_snack_meals = models.ManyToManyField(
        to="Meal",
        verbose_name=_("Afternoon snack meals"),
        related_name="afternoon_snack_meals",
        blank=True,
    )
    afternoon_snack_time = models.TimeField(_("Afternoon snack time"), blank=True, null=True)
    afternoon_snack_quality = models.CharField(_("Afternoon snack quality"), choices=MEAL_QUALITY_CHOICES,
                                               max_length=10, blank=True,
                                               null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)

    class Meta:
        ordering = ("daily_follow_up",)
        verbose_name = _("Meal daily follow-up")
        verbose_name_plural = _("Meal daily follow-ups")

    def __str__(self):
        return _("Meal: {}").format(self.daily_follow_up)


class Meal(TimeStampedModel):
    """
    Model for Meal
    """

    def upload_image_meal(self, filename):
        f, ext = os.path.splitext(filename)
        upload_to = "img/meal/{0}".format(slugify(self.name))
        return "{0}{1}".format(upload_to, ext)

    name = models.CharField(_("Name"), max_length=50)
    image = models.ImageField(_("Image"), upload_to=upload_image_meal, blank=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Meal')
        verbose_name_plural = _('Meals')

    def __str__(self):
        return self.name


class Troubleshooting(TimeStampedModel):
    """
    Model for Troubleshooting
    """
    daily_follow_up = models.OneToOneField(
        to=DailyFollowUp,
        verbose_name=_("Daily follow-up"),
        on_delete=models.CASCADE,
    )
    periods = models.ManyToManyField(
        to=Period,
        verbose_name=_("Periods"),
    )

    class Meta:
        ordering = ("daily_follow_up",)
        verbose_name = _("Troubleshooting")
        verbose_name_plural = _("Troubleshooting")

    def __str__(self):
        return _("Troubleshooting: {}").format(self.daily_follow_up)


class EarlyTroubleshooting(models.Model):
    """
    Model for EarlyTroubleshooting
    """
    child = models.ForeignKey(
        verbose_name=_("Child"),
        to=Child,
        on_delete=models.CASCADE,
    )
    date = models.DateField(verbose_name=_("Date"))
    periods = models.ManyToManyField(
        verbose_name=_("Periods"),
        to=Period,
    )

    class Meta:
        ordering = ("date",)
        verbose_name = _("Early Troubleshooting")
        verbose_name_plural = _("Early Troubleshootings")
        unique_together = ("child", "date")

    def __str__(self):
        return _("Early Troubleshooting: {} - {}").format(self.child.full_name, self.date)
