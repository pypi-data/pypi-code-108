"""Base Implementation of a Delivery Backend."""

import abc
from json import dumps
import six
import channels.layers
from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model

from . import default_settings as settings

"""import push notification"""
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.utils.text import Truncator


import json

from fcm_django.models import FCMDevice
from aparnik.utils.utils import get_request
from aparnik.contrib.settings.models import Setting
from aparnik.contrib.notifications.models import Notification
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.settings import aparnik_settings

User = get_user_model()
UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER

"""end import push notification"""
@six.add_metaclass(abc.ABCMeta)
class BaseNotificationChannel():
    """Base channel for sending notifications."""

    def __init__(self, **kwargs):
        self.notification_kwargs = kwargs

    @abc.abstractmethod
    def construct_message(self):
        """Constructs a message from notification details."""
        pass

    @abc.abstractmethod
    def notify(self, message):
        """Sends the notification."""
        pass


class ConsoleChannel(BaseNotificationChannel):
    """Dummy channel that prints to the console."""

    def construct_message(self):
        """Stringify the notification kwargs."""
        return str(self.notification_kwargs)

    def notify(self, message):
        print(message)


class BasicWebSocketChannel(BaseNotificationChannel):
    """It creates a Redis user for each user (based on their username)."""

    def _connect(self):
        channel_layer = channels.layers.get_channel_layer()
        return channel_layer

    def construct_message(self):
        """Construct message from notification details."""

        return self.notification_kwargs

    def notify(self, message):
        """
        Puts a new message on the queue.
        
        The queue is named based on the username (for Uniqueness)
        """
        uri = self.notification_kwargs['uri']

        if not uri:
            return

        channel_layer = self._connect()
        # add this moment work only with user, not guest
        async_to_sync(channel_layer.group_send)(
            uri,
            {
                "type": "send_data",
                'data': message,
            }
        )

    # # Get user instance
    # User = get_user_model()
    # source = User.objects.get(id=message['source'])
    # recipient = User.objects.get(id=message['recipient'])
    #
    # channel.queue_declare(queue=source.username)
    #
    # jsonified_messasge = dumps(message)
    # channel.basic_publish(
    #     exchange='', routing_key=recipient.username,
    #     body=jsonified_messasge
    # )


class BasicPushNotificationChannel(BaseNotificationChannel):

    def construct_message(self):
        """Construct message from notification details."""
        username_source = self.notification_kwargs['source']
        user_source_serial=None
        if username_source:
            user_source = User.objects.filter(username=username_source).first()
            user_source_serial = json.dumps(UserSummeryListSerializer(user_source,
                                                               many=False,
                                                               read_only=True,
                                                               context={'request': get_request()},
                                                               ).data,
                                     sort_keys=True,
                                     indent=1,
                                     cls=DjangoJSONEncoder
                                     ) if user_source else None
        message = {
            'title': self.notification_kwargs['short_description'],
            'body': '',
            'data': {
                'model': self.notification_kwargs['extra_data']['message'],
                'from_user': user_source_serial,
                'type': Notification.NOTIFICATION_INFO,
                'title': self.notification_kwargs['short_description'],
                'description': '',

            }
        }
        return message

    def notify(self, message):
        """
        Puts a new message on the queue.

        The queue is named based on the username (for Uniqueness)
        """
        uri = self.notification_kwargs['uri']
        recipient = self.notification_kwargs['recipient']

        if not uri and not recipient:
            return
        try:
            devices = FCMDevice.objects.filter(user__in=User.objects.filter(username=recipient)).order_by('device_id').distinct()
            sent_result = devices.send_message(
                **message
            )
            print(sent_result)
        except Exception as inst:
            print("Error happen")
            print(inst)
