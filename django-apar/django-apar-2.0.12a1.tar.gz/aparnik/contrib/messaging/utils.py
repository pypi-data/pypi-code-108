"""Utilities and helper functions."""
from aparnik.contrib.messaging.api.serializers import MessagingListSerializer
from . import MessagingError
from .models import Messaging
from .tasks import send_notification


def notify(
        uri,
        source,
        source_display_name,
        recipient,
        action,
        obj,
        short_description,
        extra_data,
        channels,
        silent=False,
):
    """Helper method to send a notification."""
    notification = Messaging(
        source=source,
        source_display_name=source_display_name,
        recipient=recipient,
        category=obj.resourcetype,
        action=action.upper(),
        obj=obj.id,
        uri=uri,
        short_description=short_description,
        channels=channels,
        extra_data=extra_data,
    )

    # If it's a not a silent notification, save the notification
    if not silent:
        notification.save()

    # Send the notification asynchronously with celery
    send_notification.delay(MessagingListSerializer(notification, many=False, read_only=True, context={''}).data)


def read(notify_id, recipient):
    """
    Helper method to read a notification.

    Raises NotificationError if the user doesn't have access
    to read the notification
    """
    notification = Messaging.objects.get(id=notify_id)

    if recipient != notification.recipient:
        raise MessagingError('You cannot read this notification')

    notification.read()
