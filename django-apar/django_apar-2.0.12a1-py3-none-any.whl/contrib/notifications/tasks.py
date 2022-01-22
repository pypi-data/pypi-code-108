"""Celery tasks."""

from __future__ import absolute_import, unicode_literals

import json
import time

from celery import shared_task
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.text import Truncator
from fcm_django.models import FCMDevice

from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.contrib.notifications.models import Notification
from aparnik.contrib.settings.models import Setting
from aparnik.contrib.users.api.views import UserSummeryListSerializer
from aparnik.utils.utils import get_request


@shared_task
def send_push_notification(chat_message_id):
    """Send chat message create notification and etc via a channel to celery."""
    time.sleep(0.2)
    notification = Notification.objects.get(pk=chat_message_id)

    icon = 'https://cdn.aparnik.com/static/website/img/logo-persian.png'
    request = get_request()
    try:
        setting = Setting.objects.get(key='LOGO_PROJECT_ICON')
        icon = setting.get_value()
    except:
        pass

    obj = notification

    model_serial = json.dumps(
        ModelListPolymorphicSerializer(
            obj.model_obj,
            many=False,
            read_only=True,
            context={'request': request},
        ).data,
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder
        ) if obj.model_obj else None

    user_serial = json.dumps(
        UserSummeryListSerializer(
            obj.from_user_obj,
            many=False,
            read_only=True,
            context={'request': request},
            ).data,
            sort_keys=True,
            indent=1,
            cls=DjangoJSONEncoder
            ) if obj.from_user_obj else None
    try:
        devices = FCMDevice.objects.filter(user__in=obj.users.all()).order_by('device_id').distinct()
        # TODO: handle response to log and etc...
        sent_result = devices.send_message(
            title=obj.title,
            body=Truncator(obj.description).words(30),
            icon=icon,
            data={
                'model': model_serial,
                'from_user': user_serial,
                'type': obj.type,
                'title': obj.title,
                'description': Truncator(obj.description).words(30),

            }
        )
        obj.sent_result = sent_result
        obj.description_for_admin = None
        obj.update_needed = False
        obj.save()
    except Exception as inst:
        obj.description_for_admin = 'type: {0}\nargs: {1}\ninstance: {2}'.format(type(inst), inst.args, inst)
        obj.save()
