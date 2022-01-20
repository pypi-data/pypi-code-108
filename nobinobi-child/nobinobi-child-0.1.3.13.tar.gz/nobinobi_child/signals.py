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

import logging
import os
from sys import stdout

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from nobinobi_child.models import *
from nobinobi_child.utils import rotate_image

GROUP_NAME = getattr(settings, "GROUP_NAME_USERS", "Users")
ADMIN_GROUP_NAME = getattr(settings, "GROUP_NAME_ADMIN", "Admin")


@receiver(post_save, sender=Child, dispatch_uid="update_image_child")
def update_image(sender, instance, **kwargs):
    if instance.picture:
        try:
            full_path = instance.picture.path
            rotate_image(full_path)
        except FileNotFoundError:
            pass


def create_group_nobinobi_child(sender, **kwargs):
    absences_type = ContentType.objects.get_for_model(Absence)
    children_type = ContentType.objects.get_for_model(Child)

    group, created = Group.objects.get_or_create(name=('%s' % GROUP_NAME))
    if created:
        logging.info('%s Group created' % GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))
        # Code to add permission to group ???
    permissions = [
        (absences_type, "add_absence"),
        (absences_type, "change_absence"),
        (absences_type, "delete_absence"),
        (absences_type, "view_absence"),
        (children_type, "view_child"),
    ]
    # Now what - Say I want to add 'Can add project' permission to new_group?
    permission_list = []
    for content_type, perm in permissions:
        permission_list.append(
            Permission.objects.get(content_type=content_type, codename=perm))

    for permission in permission_list:
        group.permissions.add(permission)
        stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))


def create_group_admin_nobinobi_child(sender, **kwargs):
    absences_type = ContentType.objects.get_for_model(Absence)
    children_type = ContentType.objects.get_for_model(Child)
    language_type = ContentType.objects.get_for_model(Language)
    absencetype_type = ContentType.objects.get_for_model(AbsenceType)
    absencegroup_type = ContentType.objects.get_for_model(AbsenceGroup)
    agegroup_type = ContentType.objects.get_for_model(AgeGroup)
    classroom_type = ContentType.objects.get_for_model(Classroom)
    classroomdayoff_type = ContentType.objects.get_for_model(ClassroomDayOff)
    childtoperiod_type = ContentType.objects.get_for_model(ChildToPeriod)
    period_type = ContentType.objects.get_for_model(Period)
    informationoftheday_type = ContentType.objects.get_for_model(InformationOfTheDay)
    allergy_type = ContentType.objects.get_for_model(Allergy)
    childtocontact_type = ContentType.objects.get_for_model(ChildToContact)
    contact_type = ContentType.objects.get_for_model(Contact)
    address_type = ContentType.objects.get_for_model(Address)
    foodrestriction_type = ContentType.objects.get_for_model(FoodRestriction)
    childspecificneed_type = ContentType.objects.get_for_model(ChildSpecificNeed)
    logchangeclassroom_type = ContentType.objects.get_for_model(LogChangeClassroom)

    group, created = Group.objects.get_or_create(name=('%s' % ADMIN_GROUP_NAME))
    if created:
        logging.info('%s Group created' % ADMIN_GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))
        # Code to add permission to group ???
    permissions = [
        (absences_type, "add_absence"),
        (absences_type, "change_absence"),
        (absences_type, "delete_absence"),
        (absences_type, "view_absence"),

        (children_type, "add_child"),
        (children_type, "change_child"),
        (children_type, "delete_child"),
        (children_type, "view_child"),

        (language_type, "add_language"),
        (language_type, "change_language"),
        (language_type, "delete_language"),
        (language_type, "view_language"),

        (absencetype_type, "add_absencetype"),
        (absencetype_type, "change_absencetype"),
        (absencetype_type, "delete_absencetype"),
        (absencetype_type, "view_absencetype"),

        (absencegroup_type, "add_absencegroup"),
        (absencegroup_type, "change_absencegroup"),
        (absencegroup_type, "delete_absencegroup"),
        (absencegroup_type, "view_absencegroup"),

        (agegroup_type, "add_agegroup"),
        (agegroup_type, "change_agegroup"),
        (agegroup_type, "delete_agegroup"),
        (agegroup_type, "view_agegroup"),

        (classroom_type, "add_classroom"),
        (classroom_type, "change_classroom"),
        (classroom_type, "delete_classroom"),
        (classroom_type, "view_classroom"),

        (classroomdayoff_type, "add_classroomdayoff"),
        (classroomdayoff_type, "change_classroomdayoff"),
        (classroomdayoff_type, "delete_classroomdayoff"),
        (classroomdayoff_type, "view_classroomdayoff"),

        (childtoperiod_type, "add_childtoperiod"),
        (childtoperiod_type, "change_childtoperiod"),
        (childtoperiod_type, "delete_childtoperiod"),
        (childtoperiod_type, "view_childtoperiod"),

        (period_type, "add_period"),
        (period_type, "change_period"),
        (period_type, "delete_period"),
        (period_type, "view_period"),

        (informationoftheday_type, "add_informationoftheday"),
        (informationoftheday_type, "change_informationoftheday"),
        (informationoftheday_type, "delete_informationoftheday"),
        (informationoftheday_type, "view_informationoftheday"),

        (allergy_type, "add_allergy"),
        (allergy_type, "change_allergy"),
        (allergy_type, "delete_allergy"),
        (allergy_type, "view_allergy"),

        (childtocontact_type, "add_childtocontact"),
        (childtocontact_type, "change_childtocontact"),
        (childtocontact_type, "delete_childtocontact"),
        (childtocontact_type, "view_childtocontact"),

        (contact_type, "add_contact"),
        (contact_type, "change_contact"),
        (contact_type, "delete_contact"),
        (contact_type, "view_contact"),

        (address_type, "add_address"),
        (address_type, "change_address"),
        (address_type, "delete_address"),
        (address_type, "view_address"),

        (foodrestriction_type, "add_foodrestriction"),
        (foodrestriction_type, "change_foodrestriction"),
        (foodrestriction_type, "delete_foodrestriction"),
        (foodrestriction_type, "view_foodrestriction"),

        (childspecificneed_type, "add_childspecificneed"),
        (childspecificneed_type, "change_childspecificneed"),
        (childspecificneed_type, "delete_childspecificneed"),
        (childspecificneed_type, "view_childspecificneed"),

        (logchangeclassroom_type, "add_logchangeclassroom"),
        (logchangeclassroom_type, "change_logchangeclassroom"),
        (logchangeclassroom_type, "delete_logchangeclassroom"),
        (logchangeclassroom_type, "view_logchangeclassroom"),

    ]
    # Now what - Say I want to add 'Can add project' permission to new_group?
    permission_list = []
    for content_type, perm in permissions:
        permission_list.append(
            Permission.objects.get(content_type=content_type, codename=perm))

    for permission in permission_list:
        group.permissions.add(permission)
        stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))
