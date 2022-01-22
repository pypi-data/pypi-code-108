"""Celery tasks."""

from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task

from aparnik.contrib.chats.api.serializers import ChatSessionMessageDetailsSerializer
from aparnik.contrib.chats.models import *
from aparnik.contrib.messaging.utils import notify
from aparnik.utils.utils import get_request


@shared_task
def send_chat_message(chat_message_id):
    """Send chat message create notification and etc via a channel to celery."""
    time.sleep(0.2)
    chat_message = ChatSessionMessage.objects.get(pk=chat_message_id)
    chat_session = chat_message.chat_session
    user = chat_message.user
    owner = chat_session.owner

    """Send notification via a channel to celery."""
    serializer = ChatSessionMessageDetailsSerializer(chat_message, many=False, read_only=True,
                                                     context={'request': get_request()})
    notify(
        uri=chat_session.uri,
        source=user,
        source_display_name=user.get_full_name(),
        recipient=None,
        action='Create',
        obj=chat_message,
        short_description='You a new message',
        extra_data={
            'uri': chat_session.uri,
            'message': serializer.data,
        },
        channels=['websocket'],
        silent=True,
    )

    """send push notification"""

    def chat_append_to_list(instance, list):
        list.append(instance)
        notify(
            uri=chat_session.uri,
            source=user,
            source_display_name=user.get_full_name(),
            recipient=member.user,
            action='Create',
            obj=chat_message,
            short_description='You a new message',
            extra_data={
                'uri': chat_session.uri,
                'message': serializer.data,
            },
            channels=['push'],
            silent=True,
        )
        return list

    # Best practise send push notification to topics but django fcm didnt support yet.
    chat_notifications = []
    members = chat_session.members.prefetch_related('user').exclude(user=user)
    for member in members:
        chat_notifications = chat_append_to_list(ChatMessageNotification(
            chat_message=chat_message,
            user=member.user,
        ), chat_notifications, )

    if owner.pk != user.pk:
        chat_notifications = chat_append_to_list(ChatMessageNotification(
            chat_message=chat_message,
            user=owner,
        ), chat_notifications, )

    ChatMessageNotification.objects.bulk_create(chat_notifications)
