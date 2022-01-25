# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible

import reversion
from tinymce.models import HTMLField

User = get_user_model()


@reversion.register()
@python_2_unicode_compatible
class Notification(models.Model):
    SIGN_COMPANY = 'SIGN_COMPANY'
    SIMPLE_OK = 'SIMPLE_OK'
    RELEASE_NOTES = 'RELEASE_NOTES'

    NOTIFICATION_CHOICES = (
        (SIGN_COMPANY, 'SIGN_COMPANY'),
        (SIMPLE_OK, 'SIMPLE_OK'),
        (RELEASE_NOTES, 'RELEASE_NOTES'),
    )
    external_id = models.IntegerField(
        null=True,
        help_text="Used to reference externally created notifications",
    )
    name = models.CharField(
        max_length=250,
        unique=True,
        help_text="Used to reference notification, shown in title for some looks",
    )
    message = HTMLField(
        help_text="Full message as shown to user",
    )
    expires = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text="Notification will not be shown after this time.",
    )
    attachment = models.FileField(
        default=None,
        blank=True,
        null=True,
    )
    active_from = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
    )
    needs_approval = models.BooleanField(
        default=False,
        help_text="Set this field if approval is necessary, see snooze time.",
    )
    snooze_lock = models.IntegerField(
        default=None,
        null=True,
        blank=True,
    )
    snooze_time = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="If user dismisses message (when relevant), message is shown again after this many days.",
    )  # Days
    recipients = models.ManyToManyField(
        User,
        through='UserNotification',
        default=None,
        blank=True,
    )
    send_email = models.BooleanField(
        default=False,
    )
    groups = models.ManyToManyField(
        Group,
        default=None,
        blank=True,
    )
    # SIGN_COMPANY set as default because it's the only one current existing, safe to remove
    look = models.CharField(
        max_length=50,
        choices=NOTIFICATION_CHOICES,
        default=SIMPLE_OK,
        help_text="This controls the appearance of the notification.",
    )
    image = models.ImageField(
        upload_to='notification_imgs',
        null=True,
        blank=True,
        help_text="Image to accompany notification (optional)",
    )
    display_only_if_url_path_matches_regex = models.CharField(
        max_length=64,
        default='.*',
        null=False,
        blank=False,
        help_text='Only display this notification if the provided regex matches the url-path',
    )

    KEY_FORMAT = "{}:{}"
    UNSEEN_KEY = 'notifications_unseen'

    def __str__(self):
        return self.name

    @classmethod
    def notification_key(cls, user):
        return cls.KEY_FORMAT.format(cls.UNSEEN_KEY, user.id)

    @classmethod
    def unseen(cls, user):
        notifications = cache.get(cls.notification_key(user), default={})
        for user_notif_id in notifications:
            # To make sure cache is up to date for existing notifications
            # before cookies are populated.
            upd_notif = cache.get(cls.notification_key(user), default={})
            try:
                UserNotification.objects.get(id=user_notif_id).update_unseen_cache(unseen=upd_notif)
            except UserNotification.DoesNotExist:
                pass

        updated_notifications = cache.get(cls.notification_key(user), default={})
        return updated_notifications

    def create_usernotifications_for_groups(self, database_name=None):
        for group in self.groups.all():
            for user in group.user_set.all():
                if database_name is not None:
                    UserNotification.objects.using(database_name).get_or_create(notification=self, user=user)
                else:
                    UserNotification.objects.get_or_create(notification=self, user=user)

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        using = kwargs.get('using', None)
        self.create_usernotifications_for_groups(database_name=using)


@reversion.register()
@python_2_unicode_compatible
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    next_display = models.DateTimeField(default=None, null=True, blank=True)
    answer = models.NullBooleanField(default=None, null=True, blank=True)
    answer_string = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return "{} - {} - seen:{} - answer:{} - answer_string:{}".format(
            self.notification.name,
            self.user.username,
            self.seen,
            self.answer,
            self.answer_string
        )

    def update_unseen_cache(self, unseen=None):
        if unseen is None:
            unseen = Notification.unseen(self.user)

        if (self.seen and self.answer) or (
            self.notification.expires is not None and self.notification.expires < datetime.datetime.now()
        ):
            if self.id in unseen:
                del unseen[self.id]
        elif self.next_display:
            unseen[self.id] = self.next_display
        else:
            # 10 Minute in the past to make up for discrepancy between client time and server time
            unseen[self.id] = datetime.datetime.now() - datetime.timedelta(minutes=10)
        if len(unseen) == 0:
            return cache.delete(Notification.notification_key(self.user))
        return cache.set(Notification.notification_key(self.user), unseen, timeout=None)

    def save(self, *args, **kwargs):
        if self.answer is not None:
            self.seen = True
        if self.seen and not self.answer:
            snooze_time = self.notification.snooze_time or 1
            self.next_display = datetime.datetime.now() + datetime.timedelta(days=snooze_time)
        super(UserNotification, self).save(*args, **kwargs)
        self.update_unseen_cache()

    def delete(self, *args, **kwargs):
        super(UserNotification, self).delete(*args, **kwargs)
        cache.delete(Notification.notification_key(self.user))

    @staticmethod
    def update_for_user(user):
        uns = user.usernotification_set.exclude(answer=True).filter(
            Q(notification__expires=None) | Q(notification__expires__gt=datetime.datetime.now())
        )

        # Here to ensure cache is up to date
        for un in uns:
            un.update_unseen_cache()
