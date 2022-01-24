# -*- coding: UTF-8 -*-
# Copyright 2020-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging; logger = logging.getLogger(__name__)
import json
from django.utils.timezone import now
from lino.api import rt, dd

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None


NOTIFICATION = "NOTIFICATION"
CHAT = "CHAT"

NOTIFICATION_TYPES = [
    NOTIFICATION, CHAT
]


def send_notification(user=None, primary_key=None, subject=None, body=None,
    created=None, action_url=None, action_title="OK"):
    """

    `action_url` : the URL to show when user clicks on the
    OK button of their desktop notification.

    """

    created = created.strftime("%a %d %b %Y %H:%M")

    if dd.plugins.notify.use_websockets:
        # importing channels at module level would cause certain things to fail
        # when channels isn't installed, e.g. `manage.py prep` in `lino_book.projects.workflows`.
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        msg = dict(
            type=NOTIFICATION,
            subject=subject,
            id=primary_key,
            body=body,
            created=created,
        )

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(str(user.pk),
                                                    {"type": "send_notification",  # method name in consumer
                                                     "text": json.dumps(msg)})  # data
        except Exception as E:
            logger.exception(E)

    elif dd.plugins.notify.use_push_api:
        data = dict(action_url=action_url, subject=subject, body=body, action_title=action_title)
        logger.info("Push to %s : %s", user or "everyone", data)
        kwargs = dict(
            data=json.dumps(data),
            vapid_private_key=dd.plugins.notify.vapid_private_key,
            vapid_claims={
                'sub': "mailto:{}".format(dd.plugins.notify.vapid_admin_email)
            }
        )
        if user is None:
            subs = rt.models.notify.Subscription.objects.all()
        else:
            subs = rt.models.notify.Subscription.objects.filter(user=user)
        for sub in subs:
            sub_info = {
                'endpoint': sub.endpoint,
                'keys': {
                    'p256dh': sub.p256dh,
                    'auth': sub.auth,
                },
            }
            try:
                req = webpush(subscription_info=sub_info, **kwargs)
            except WebPushException as e:
                if e.response.status_code == 410:
                    sub.delete()
                else:
                    raise e


def send_global_chat(message):
    """
    Sends a WS message to each user using ChatProps"""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    for chat in message.chatProps.all():
        msg = dict(
            type=CHAT,
            chat=chat.serialize())

        try:
            assert bool(chat.user)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(str(chat.user.pk),
                                                    {"type": "send_notification",
                                                     # just pointer to method name in consumer
                                                     "text": json.dumps(msg)})  # data
            chat.sent = now()
            chat.save()
        except Exception as E:
            logger.exception(E)
