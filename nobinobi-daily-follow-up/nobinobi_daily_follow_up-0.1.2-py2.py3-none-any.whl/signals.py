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


import datetime
import datetime as dt
import logging
import sys
from sys import stdout

from datetimerange import DateTimeRange
from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from nobinobi_child.models import ChildToPeriod

from nobinobi_daily_follow_up.models import *

GROUP_NAME = getattr(settings, "GROUP_NAME_USERS", "Users")
ADMIN_GROUP_NAME = getattr(settings, "GROUP_NAME_ADMIN", "Admin")


def create_group_nobinobi_daily_follow_up(sender, **kwargs):
    presence_type = ContentType.objects.get_for_model(Presence)
    daily_follow_up_type = ContentType.objects.get_for_model(DailyFollowUp)
    reception_type = ContentType.objects.get_for_model(Reception)
    mealdailyfollowup_type = ContentType.objects.get_for_model(MealDailyFollowUp)
    nap_type = ContentType.objects.get_for_model(Nap)
    diaperchange_type = ContentType.objects.get_for_model(DiaperChange)
    lotiondailyfollowup_type = ContentType.objects.get_for_model(LotionDailyFollowUp)
    activity_type = ContentType.objects.get_for_model(Activity)
    medication_type = ContentType.objects.get_for_model(Medication)

    group, created = Group.objects.get_or_create(name=('%s' % GROUP_NAME))
    if created:
        logging.info('%s Group created' % GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))
        # Code to add permission to group ???
    permissions = [
        (presence_type, "add_presence"),
        (presence_type, "change_presence"),
        (presence_type, "delete_presence"),
        (presence_type, "view_presence"),
        (daily_follow_up_type, "add_dailyfollowup"),
        (daily_follow_up_type, "change_dailyfollowup"),
        (daily_follow_up_type, "delete_dailyfollowup"),
        (daily_follow_up_type, "view_dailyfollowup"),
        (reception_type, "change_reception"),
        (mealdailyfollowup_type, "change_mealdailyfollowup"),
        (nap_type, "add_nap"),
        (nap_type, "change_nap"),
        (nap_type, "delete_nap"),
        (diaperchange_type, "add_diaperchange"),
        (diaperchange_type, "change_diaperchange"),
        (diaperchange_type, "delete_diaperchange"),
        (lotiondailyfollowup_type, "add_lotiondailyfollowup"),
        (lotiondailyfollowup_type, "change_lotiondailyfollowup"),
        (lotiondailyfollowup_type, "delete_lotiondailyfollowup"),
        (activity_type, "add_activity"),
        (activity_type, "change_activity"),
        (activity_type, "delete_activity"),
        (medication_type, "add_medication"),
        (medication_type, "change_medication"),
        (medication_type, "delete_medication"),
    ]
    # Now what - Say I want to add 'Can add project' permission to new_group?
    permission_list = []
    for content_type, perm in permissions:
        permission_list.append(
            Permission.objects.get(content_type=content_type, codename=perm))

    for permission in permission_list:
        group.permissions.add(permission)
        stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))


def create_group_admin_nobinobi_daily_follow_up(sender, **kwargs):
    group, created = Group.objects.get_or_create(name=('%s' % ADMIN_GROUP_NAME))
    if created:
        logging.info('%s Group created' % ADMIN_GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))

    models = [Presence, DailyFollowUp, Reception, TypeActivity, ActivityGroup, Lotion, DailyFollowUpToMedication,
              TypeMedication, Meal, GiveMedication, MealDailyFollowUp, Nap, DiaperChange, LotionDailyFollowUp, Activity,
              Medication, Troubleshooting, EarlyTroubleshooting]
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        all_permissions = Permission.objects.filter(content_type=content_type)
        for permission in all_permissions:
            group.permissions.add(permission)
            stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))


def auto_delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


def auto_delete_image_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).image
        if not old_file.name:
            raise sender.DoesNotExist
    except sender.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


def auto_delete_attachment_on_delete(sender, instance, **kwargs):
    """
    Deletes attachment from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.attachment:
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)


def auto_delete_attachment_on_change(sender, instance, **kwargs):
    """
    Deletes old attachment from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).attachment
        if not old_file.path:
            raise ValueError
    except sender.DoesNotExist:
        return False
    except ValueError:
        return False

    new_file = instance.attachment
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


def medication_on_daily_follow_up(sender, instance, **kwargs):
    medications = Medication.objects.filter(child=instance.presence.child, from_date__lte=instance.presence.date,
                                            end_date__gte=instance.presence.date)
    now = timezone.localtime()
    for medication in medications:
        dtm, created = DailyFollowUpToMedication.objects.get_or_create(
            medication=medication,
            daily_follow_up=instance
        )
        givemedication_type = ContentType.objects.get_for_model(GiveMedication)
        gms = GiveMedication.objects.filter(medication=medication, date=now.date())
        for gm in gms:
            # activate notification for day
            notifications = Notification.objects.filter(actor_content_type=givemedication_type, actor_object_id=gm.id,
                                                        public=False, timestamp__lte=now)
            for notification in notifications:
                notification.public = True
                notification.save()


def delete_notification_after_delete_givemedication(sender, instance, **kwargs):
    givemedication_type = ContentType.objects.get_for_model(sender)
    try:
        gms = Notification.objects.filter(actor_object_id=instance.id, actor_content_type=givemedication_type, )
        if gms.count() == 0:
            raise Notification.DoesNotExist
    except Notification.DoesNotExist:
        pass
    else:
        for gm in gms:
            gm.delete()
    sys.stdout.write(_("Notification for give medication was deleted.\n"))


def create_notification_after_save_givemedication(sender, instance, **kwargs):
    gm = instance
    mytime = dt.datetime.strptime(str(gm.give_hour), '%H:%M:%S').time()
    tz = timezone.get_current_timezone()
    mydatetime = tz.localize(dt.datetime.combine(instance.date, mytime))

    is_same_day = True if mydatetime.date() == timezone.localtime().date() else False
    classroom_users = instance.medication.child.classroom.allowed_login.all()
    classroom_group_users = instance.medication.child.classroom.allowed_group_login.all()
    givemedication_type = ContentType.objects.get_for_model(sender)
    if not instance.given_hour and not instance.staff:
        if mydatetime.date() >= timezone.localtime().date() and mydatetime.isoweekday() not in [6, 7]:
            for user in classroom_users:
                create_notification(givemedication_type, gm, instance, is_same_day, mydatetime, user)

            for group in classroom_group_users:
                for user in group.user_set.all():
                    create_notification(givemedication_type, gm, instance, is_same_day, mydatetime, user)

    elif instance.given_hour and instance.staff:
        try:
            notifs = Notification.objects.filter(actor_content_type=givemedication_type,
                                                 actor_object_id=gm.id, level="warning")
            if notifs.count() == 0:
                raise Notification.DoesNotExist
        except Notification.DoesNotExist:
            pass
        else:
            for notif in notifs:
                notif.delete()
    sys.stdout.write(_("Notification for give medication was created.\n"))


def create_notification(givemedication_type, gm, instance, is_same_day, mydatetime, user):
    notif, created = Notification.objects.get_or_create(recipient=user,
                                                        actor_content_type=givemedication_type,
                                                        actor_object_id=gm.id, level="warning",
                                                        defaults={
                                                            "public": is_same_day,
                                                            "timestamp": mydatetime,
                                                            "description": "{} - {}".format(
                                                                instance.medication.type_medication,
                                                                instance.medication.comment),
                                                            "verb": "{} {}".format(_("Give medication"),
                                                                                   instance.medication.child.full_name),
                                                        })
    if not created:
        if is_same_day:
            notif.public = True
        notif.timestamp = mydatetime
        notif.save()


def create_troubleshooting_in_daily_follow_up(sender, instance, **kwargs):
    today = instance.presence.date
    classroom = instance.presence.classroom

    # get general periods for this weekday and this classroom
    periods = list(Period.objects.filter(weekday=today.isoweekday()).order_by("order"))
    # get timerange now
    if not instance.presence.departure_time:
        time_range = DateTimeRange(datetime.datetime.combine(today, instance.presence.arrival_time),
                                   datetime.datetime.combine(today, instance.presence.arrival_time))
    else:
        time_range = DateTimeRange(datetime.datetime.combine(today, instance.presence.arrival_time),
                                   datetime.datetime.combine(today, instance.presence.departure_time))
    periods_in_range = []
    # get period interaction from arrival_time
    for period in periods:
        period_range = DateTimeRange(datetime.datetime.combine(today, period.start_time),
                                     datetime.datetime.combine(today, period.end_time))

        if time_range.is_intersection(period_range):
            try:
                ChildToPeriod.objects.filter(
                    child=instance.presence.child,
                    child__status=Child.STATUS.in_progress,
                    start_date__lte=today,
                    end_date__gte=today,
                    period=period,
                )
            except ChildToPeriod.DoesNotExist:
                periods_in_range.append(period.id)

    if periods_in_range:
        ts, created = Troubleshooting.objects.get_or_create(daily_follow_up=instance)
        ts.periods.set(periods_in_range)
    else:
        try:
            ts = Troubleshooting.objects.get(daily_follow_up=instance)
        except Troubleshooting.DoesNotExist:
            pass
        else:
            ts.delete()

    # sinon trouble
    # on check les early troubleshooting

    try:
        early_troubleshooting = EarlyTroubleshooting.objects.get(date=today, child=instance.presence.child)
    except EarlyTroubleshooting.DoesNotExist:
        pass
    else:
        ts, created = Troubleshooting.objects.get_or_create(daily_follow_up=instance)
        period_list = list(early_troubleshooting.periods.all())
        ts.periods.set(period_list)
