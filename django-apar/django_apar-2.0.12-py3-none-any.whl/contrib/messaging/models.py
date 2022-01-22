"""Messaging model."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model

from .fields import JSONField, ListField


class MessagingQuerySet(models.QuerySet):
    """Messagings QuerySet."""

    def all_unread(self):
        """Return all unread notifications."""

        return self.filter(is_read=False)

    def all_read(self):
        """Return all read notifications."""

        return self.filter(is_read=True)


class Messaging(models.Model):
    """
    Model for notifications.

    Parameters:
    ----------
    source: A ForeignKey to Django's User model
        (Can be null if it's not a User to User Messaging)

    source_display_name: A User Friendly name
        for the source of the notification.

    recipient: The Recipient of the notification.
        It's a ForeignKey to Django's User model.

    action: Verbal action for the notification
        E.g Sent, Cancelled, Bought e.t.c

    obj: The id of the object associated with the notification
        (Can be null)

    short_description: The body of the notification.

    url: The url of the object associated with the notification
        (Can be null)
    channels: Channel(s) that were/was used to deliver the message

    extra_data: Extra information that was passed in the notification
        (Optional but default value is an empty dict {})
    """

    User = settings.AUTH_USER_MODEL

    class Meta:
        """Specify ordering for notifications."""
        ordering = ('-id',)

    source = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    source_display_name = models.CharField(max_length=150, null=True)
    recipient = models.ForeignKey(
        User, related_name='notifications', null=True, 
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    obj = models.IntegerField(null=True, blank=True)
    uri = models.CharField(max_length=255, null=True, verbose_name=_('URI'))
    url = models.URLField(null=True, blank=True)
    short_description = models.CharField(max_length=100)
    channels = ListField(max_length=200)
    extra_data = JSONField(default={})
    is_read = models.BooleanField(default=False)

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    # register queryset
    objects = MessagingQuerySet.as_manager()

    def __str__(self):
        if self.source:
            res = '{}: {} {} {} => {}'.format(
                self.category, self.source, self.action,
                self.short_description, self.recipient
            )
        else:
            res = self.short_description

        return res

    def read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()
