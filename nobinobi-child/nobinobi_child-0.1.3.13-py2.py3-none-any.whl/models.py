# -*- coding: utf-8 -*-

#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from model_utils import Choices
from model_utils.fields import StatusField, SplitField
from model_utils.models import TimeStampedModel, StatusModel
from nobinobi_child.utils import get_unique_slug
from nobinobi_core.models import Organisation
from nobinobi_staff.models import Staff
from phonenumber_field.modelfields import PhoneNumberField

WEEKDAY_CHOICES = Choices(
    (1, "monday", _("Monday")),
    (2, "tuesday", _("Tuesday")),
    (3, "wednesday", _("Wednesday")),
    (4, "thursday", _("Thursday")),
    (5, "friday", _("Friday")),
    (6, "saturday", _("Saturday")),
    (7, "sunday", _("Sunday")),
)

TYPE_PERIOD_CHOICES = Choices(
    ("morning", _("Morning")),
    ("afternoon", _("Afternoon")),
    ("day", _("Day")),
)


class Child(StatusModel, TimeStampedModel):
    def upload_picture_child(self, filename):
        f, ext = os.path.splitext(filename)
        upload_to = "child/%s/" % self.slug
        return '%s%s%s' % (upload_to, uuid.uuid4().hex, ext)

    STATUS = Choices(
        ("in_progress", _('In progress')),
        ("archived", _('Archived')),
        ("future", _('Future'))
    )
    GENDER_CHOICES = Choices(
        ("boy", _("Boy")),
        ("girl", _("Girl")),
        ("other", _("Other")),
        ("unknown", _("Unknown")),
    )
    """
    Model to store child
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("First name"), max_length=100)
    last_name = models.CharField(_("Last name"), max_length=100)
    usual_name = models.CharField(_("Usual name"), max_length=100, unique=True)
    gender = StatusField(_("Gender"), choices_name="GENDER_CHOICES", blank=False, null=True)
    slug = models.SlugField(_("Slug"))
    picture = models.ImageField(_("Picture"), upload_to=upload_picture_child, blank=True, null=True)
    birth_date = models.DateField(_("Birth date"), blank=True, null=True)
    languages = models.ManyToManyField(
        to="Language",
        verbose_name=_("Languages"),
        related_name="languages",
        blank=True
    )
    red_list = models.CharField(_("Red list"), max_length=255, blank=True, null=True)
    comment = models.CharField(_("Comment"), max_length=255, blank=True, null=True)
    nationality = models.CharField(_("Child nationality"), max_length=255, blank=True, null=True)

    # Sibling
    sibling_name = models.CharField(_("Sibling's name and first name"), max_length=50, blank=True, null=True)
    sibling_birth_date = models.DateField(_("Sibling birth date"), null=True, blank=True)
    sibling_institution = models.CharField(_("Sibling's institution"), max_length=100, blank=True, null=True)

    renewal_date = models.DateField(_("Renewal date"), blank=True, null=True)
    usage_paracetamol = models.BooleanField(_("Usage paracetamol"), blank=False, null=True)
    usage_homeopathy = models.BooleanField(_("Usage homeopathy"), blank=False, null=True)
    healthy_child = models.BooleanField(_("Healthy child"), blank=False, null=True)
    good_development = models.BooleanField(_("Good development"), blank=False, null=True)
    specific_problem = models.CharField(_("Specific problem"), max_length=255, blank=True, null=True)
    vaccination = models.BooleanField(_("Vaccination"), blank=False, null=True)
    health_insurance = models.CharField(_("Health Insurance"), max_length=255, blank=True, null=True)

    pediatrician_contact = models.BooleanField(_("Pediatrician contact"), blank=True, null=True)

    pediatrician = models.ForeignKey(
        to="Contact",
        verbose_name=_("Pediatrician"),
        on_delete=models.PROTECT,
        related_name="pediatrician",
        blank=True,
        null=True
    )

    classroom = models.ForeignKey(
        to="Classroom",
        verbose_name=getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom")),
        on_delete=models.SET_NULL,
        related_name="classroom",
        db_index=True,
        blank=True,
        null=True,
    )

    next_classroom = models.ForeignKey(
        to="Classroom",
        verbose_name=_("Next classroom"),
        on_delete=models.SET_NULL,
        related_name="next_classroom",
        blank=True,
        null=True,
    )
    date_next_classroom = models.DateField(verbose_name=_("Date next classroom"), blank=True, null=True)

    age_group = models.ForeignKey(
        to="AgeGroup",
        verbose_name=_("Age group"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    staff = models.ForeignKey(
        to=Staff,
        verbose_name=_("Staff"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    food_restrictions = models.ManyToManyField(
        to="FoodRestriction",
        verbose_name=_("Food restrictions"),
        related_name="food_restrictions",
        blank=True,
    )
    allergies = models.ManyToManyField(
        to="Allergy",
        verbose_name=_("Allergies"),
        related_name="allergies",
        blank=True,
    )
    periods = models.ManyToManyField(
        to="Period",
        through="ChildToPeriod",
        through_fields=("child", "period"),
        verbose_name=_("Periods"),
        related_name="periods",
        blank=True,
    )
    contacts = models.ManyToManyField(
        to="Contact",
        through="ChildToContact",
        through_fields=("child", "contact"),
        verbose_name=_("Contacts"),
        related_name="contacts",
        blank=True,
    )

    class Meta:
        ordering = ('first_name', 'last_name', "created",)
        unique_together = ("first_name", "last_name", "birth_date")
        verbose_name = _('Child')
        verbose_name_plural = _('Children')

    def __str__(self):
        return "{}".format(self.full_name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # set slug, title field
        self.slug = get_unique_slug(self, 'full_name', 'slug')
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.usual_name = self.usual_name.title()
        return super(Child, self).save()

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    full_name.fget.short_description = _("Full name")

    @property
    def is_active(self):
        # return true if child is in progress else false
        return True if self.status == self.STATUS.in_progress else False

    def get_contacts_phone(self):
        dict_contacts = {}
        for oc in self.childtocontact_set.all():
            dict_contacts[oc] = {
                "link_with_child": oc.link_with_child,
                "phone": oc.contact.phone,
                "mobile_phone": oc.contact.mobile_phone,
                "professional_phone": oc.contact.professional_phone,
                "order": oc.order
            }
        return dict_contacts

    def get_now_classroom(self):
        now = timezone.localdate()
        if self.has_replacement_classroom(now):
            classroom = self.get_replacement_classroom(now)
        else:
            classroom = self.classroom
        return classroom

    def has_replacement_classroom(self, date):
        from django.db.models import Q
        rc = self.replacementclassroom_set.filter(
            Q(end_date__gte=date) | Q(end_date__isnull=True),
            archived=False,
            from_date__lte=date,
        )
        if rc.count() == 0:
            return False
        else:
            return True

    def get_replacement_classroom(self, date):
        from django.db.models import Q
        try:
            rc = self.replacementclassroom_set.get(
                Q(end_date__gte=date) | Q(end_date__isnull=True),
                archived=False,
                from_date__lte=date,
            )
        except self.replacementclassroom_set.DoesNotExist:
            return False
        except self.replacementclassroom_set.MultipleObjectsReturned:
            return False
        else:
            return rc.classroom

class Language(TimeStampedModel):
    """
    Models to store language
    """
    name = models.CharField(_("Name"), max_length=50, unique=True)

    class Meta:
        ordering = ("name", "created",)
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        # return name of language
        return self.name


class Absence(TimeStampedModel):
    """
    Models to store child absence
    """
    child = models.ForeignKey(
        to=Child,
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(verbose_name=_("Start date"))
    end_date = models.DateTimeField(verbose_name=_("End date"))
    type = models.ForeignKey(
        to="AbsenceType",
        verbose_name=_("Type"),
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ('start_date', 'end_date', 'child',)
        verbose_name = _('Absence')
        verbose_name_plural = _('Absences')

    def __str__(self):
        return "{} {} - {} - {}".format(self.start_date, self.end_date, self.child, self.type)


class AbsenceType(TimeStampedModel):
    """
    Models to store type of absence
    """
    name = models.CharField(_("Name"), max_length=50)
    group = models.ForeignKey(
        to="AbsenceGroup",
        verbose_name=_("Group"),
        on_delete=models.PROTECT,
    )
    order = models.PositiveIntegerField(_("Order"))

    class Meta:
        ordering = ('order', "group", "name")
        verbose_name = _('Absence type')
        verbose_name_plural = _('Absence types')

    def __str__(self):
        return self.name


class AbsenceGroup(TimeStampedModel):
    """
    Models to store group for absence type
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Absence group')
        verbose_name_plural = _('Absence groups')

    def __str__(self):
        return self.name


class AgeGroup(TimeStampedModel):
    """
    Models to store age group
    """
    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("Slug"))
    order = models.PositiveIntegerField(_("Order"), unique=True)
    from_date = models.DateField(_("From date"))
    end_date = models.DateField(_("End date"))

    class Meta:
        ordering = ('order', 'name',)
        verbose_name = _('Age group')
        verbose_name_plural = _('Age groups')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # set slug unique
        self.slug = get_unique_slug(self, 'name', 'slug')
        # set name in title
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Classroom(TimeStampedModel):
    """
    Models to store classroom
    """
    OPERATION_MODE = Choices(
        ("creche", _("Creche")),
        ("kindergarten", _("Kindergarten"))
    )

    name = models.CharField(_("Name"), unique=True, max_length=50)
    slug = models.SlugField(_("Slug"), unique=True)
    order = models.PositiveIntegerField(_("Order"), unique=True)
    capacity = models.PositiveIntegerField(_("Capacity"), default=20)
    mode = StatusField(verbose_name=_("Mode"), choices_name="OPERATION_MODE", default=OPERATION_MODE.creche,
                       max_length=15)
    allowed_login = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_("Allowed login"),
        related_name="classroom_login",
        blank=True
    )
    allowed_group_login = models.ManyToManyField(
        to=Group,
        verbose_name=_("Allowed group login"),
        related_name="classroom_group_login",
        blank=True
    )
    organisation = models.ForeignKey(
        to=Organisation,
        verbose_name=_("Organisation"),
        on_delete=models.PROTECT,
        blank=False,
        null=True
    )

    class Meta:
        ordering = ('order', 'name',)
        verbose_name = getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom"))
        verbose_name_plural = getattr(settings, 'NAME_CLASSROOMS_DISPLAY', _("Classrooms"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # set slug unique
        self.slug = get_unique_slug(self, 'name', 'slug')
        # set name in title
        self.name = self.name.title()
        super().save(*args, **kwargs)


class ClassroomDayOff(TimeStampedModel):
    """
    Models to store the day off classroom
    """

    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name=_("Weekday"))
    classrooms = models.ManyToManyField(
        to=Classroom,
        verbose_name=getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom")),
    )

    class Meta:
        ordering = ('weekday',)
        verbose_name = _('Classroom day off')
        verbose_name_plural = _('Classrooms days off')

    def __str__(self):
        return self.get_weekday_display()


class ChildToPeriod(TimeStampedModel):
    """
    Models between child and period to store date
    """
    child = models.ForeignKey(
        to="Child",
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
    )
    period = models.ForeignKey(
        to="Period",
        verbose_name=_("Period"),
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    class Meta:
        ordering = ('start_date', 'end_date', 'child', "period")
        verbose_name = _('Child to period')
        verbose_name_plural = _('Children to periods')

    def __str__(self):
        return "{} {} - {} - {}".format(self.start_date, self.end_date, self.child, self.period)


class Period(TimeStampedModel):
    """
    Models to store period
    """
    name = models.CharField(_("Name"), max_length=50)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name=_("Weekday"))
    order = models.PositiveIntegerField(_("Order"))
    start_time = models.TimeField(_("Start time"), blank=False, null=True)
    end_time = models.TimeField(_("End time"), blank=False, null=True)
    type = models.CharField(max_length=20, choices=TYPE_PERIOD_CHOICES, verbose_name=_("Type"),
                            default=TYPE_PERIOD_CHOICES.morning)
    max_child = models.PositiveIntegerField(_("Max child"), blank=True, null=True)

    class Meta:
        ordering = ("weekday", 'order', "name",)
        unique_together = ("weekday", "order")
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')

    def __str__(self):
        return "{} {}".format(self.get_weekday_display(), self.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.title()
        return super(Period, self).save(force_insert=False, force_update=False, using=None,
                                        update_fields=None)


class InformationOfTheDay(TimeStampedModel):
    title = models.CharField(_("Title"), max_length=50)
    classrooms = models.ManyToManyField(
        to=Classroom,
        verbose_name=getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom")),
        related_name="classrooms"
    )
    start_date = models.DateTimeField(_("Start date"))
    end_date = models.DateTimeField(_("End date"))
    content = SplitField(_("Content"))

    class Meta:
        ordering = ('start_date', 'end_date',)
        verbose_name = _('Information of the day')
        verbose_name_plural = _('Informations of the day')

    def __str__(self):
        return "IOTD: {} - {} > {}".format(self.title, self.start_date, self.end_date)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.title = self.title.title()
        return super(InformationOfTheDay, self).save(force_insert=False, force_update=False, using=None,
                                                     update_fields=None)


class Allergy(TimeStampedModel):
    """
    Models to store allergy
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Allergy')
        verbose_name_plural = _('Allergies')

    def __str__(self):
        return self.name


class ChildToContact(TimeStampedModel):
    """
    Models between child and contact to store type
    """
    child = models.ForeignKey(
        to="Child",
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
    )
    contact = models.ForeignKey(
        to="Contact",
        verbose_name=_("Contact"),
        on_delete=models.CASCADE,
    )
    link_with_child = models.CharField(verbose_name=_("Link with child"),
                                       help_text=_("Type contact: Example Father, Mother ..."), max_length=50)
    order = models.PositiveIntegerField(verbose_name=_('Order'))

    class Meta:
        ordering = ('order', "child",)
        verbose_name = _('Child to contact')
        verbose_name_plural = _('Children to contacts')

    def __str__(self):
        return self.link_with_child


class Contact(TimeStampedModel):
    """
    Models to store contacts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("First name"), max_length=100)
    last_name = models.CharField(_("Last name"), max_length=100)
    address = models.ForeignKey(
        to="Address",
        verbose_name=_("Address"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    email = models.EmailField(_("Email"), blank=True, null=True, )
    phone = PhoneNumberField(verbose_name=_("Phone"))
    mobile_phone = PhoneNumberField(verbose_name=_("Mobile phone"), blank=True, null=True)
    professional_phone = PhoneNumberField(verbose_name=_("Professional phone"), blank=True, null=True)
    organisation = models.CharField(_("Organisation"), max_length=100, blank=True, null=True)
    function = models.CharField(_("Function"), max_length=100, blank=True, null=True)
    authorized_pick_up_child = models.BooleanField(_("Contact authorized to pick up the child."), blank=False,
                                                   null=True)
    to_contact_if_needed = models.BooleanField(_("To contact if needed"), blank=False, null=True)
    reside_with_child = models.BooleanField(_('Reside with child'), default=True)
    parental_authority = models.BooleanField(_("Parental authority"), default=True)

    class Meta:
        ordering = ('first_name', 'last_name',)
        unique_together = ("first_name", "last_name", "phone")
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class Address(TimeStampedModel):
    """
    Models to store the address from contacts
    """
    street = models.CharField(_("Street"), max_length=100)
    zip = models.PositiveIntegerField(_("ZIP"))
    city = models.CharField(_("City"), max_length=50)
    country = models.CharField(_("Country"), max_length=50, default=_("Switzerland"))

    class Meta:
        ordering = ('country', 'zip', 'city', 'street')
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return "{}, {} {}, {}".format(self.street, self.zip, self.city, self.country)


class FoodRestriction(TimeStampedModel):
    """
    Models to store Food restriction
    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Food restriction')
        verbose_name_plural = _('Food restrictions')

    def __str__(self):
        return self.name


class ChildSpecificNeed(TimeStampedModel):
    """
    Models to store Child with specific problem
    """

    def upload_attachment_child(self, filename):
        f, ext = os.path.splitext(filename)
        upload_to = "child/%s/special/" % self.child.slug
        return '%s%s%s' % (upload_to, uuid.uuid4().hex, ext)

    problem = SplitField(_("Problem"))
    ihp = models.BooleanField(_("Individual home project"), default=True)
    attachment = models.FileField(_("Attachment"), upload_to=upload_attachment_child, blank=True, null=True)
    measure_take = SplitField(_("Measure to take"))
    child = models.OneToOneField(
        to="Child",
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('child',)
        verbose_name = _('Child specific need')
        verbose_name_plural = _('Children specific needs')

    def __str__(self):
        return self.child.full_name


class LogChangeClassroom(TimeStampedModel):
    """
    Models to store the change classroom for child
    """
    child = models.ForeignKey(
        to=Child,
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
    )
    classroom = models.ForeignKey(
        to=Classroom,
        verbose_name=getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom")),
        on_delete=models.SET_NULL,
        related_name="log_change_classroom",
        blank=True,
        null=True,
    )
    next_classroom = models.ForeignKey(
        to=Classroom,
        verbose_name=_("Next classroom"),
        on_delete=models.SET_NULL,
        related_name="log_change_next_classroom",
        blank=False,
        null=True
    )
    date = models.DateField(_("Date"))

    class Meta:
        ordering = ("date",)
        unique_together = ("child", "classroom")
        verbose_name = _("Log change classroom")
        verbose_name_plural = _("Logs changed classrooms")

    def __str__(self):  # __unicode__ on Python 2
        return '%s | %s -> %s | %s' % (self.child, self.classroom, self.next_classroom, self.date)


class ReplacementClassroom(TimeStampedModel):
    """
    Models to store the remplacement for classroom for child
    """
    from_date = models.DateField(_("From date"))
    end_date = models.DateField(_("End date"), blank=True, null=True)
    archived = models.BooleanField(_("Archived"), default=False)
    classroom = models.ForeignKey(
        to=Classroom,
        verbose_name=getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom")),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    child = models.ForeignKey(
        to=Child,
        verbose_name=_("Child"),
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('from_date', "classroom")
        verbose_name = _('Remplacement Classroom')
        verbose_name_plural = _('Remplacements Classroom')

    def __str__(self):
        return "{} - {} | {}".format(self.from_date, self.end_date, self.classroom.name)

    def save(self, *args, **kwargs):
        now = timezone.localdate()
        if (self.from_date and self.end_date) and self.end_date < now:
            self.archived = True
        elif (self.archived and not self.end_date) or (self.archived and self.end_date > now):
            self.archived = False
        super(ReplacementClassroom, self).save(*args, *kwargs)
