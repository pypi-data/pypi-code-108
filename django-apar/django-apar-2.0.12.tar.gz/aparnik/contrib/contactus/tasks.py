"""Celery tasks."""

from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task

from aparnik.contrib.chats.api.serializers import ChatSessionMessageDetailsSerializer
from aparnik.contrib.contactus.api.serializers import ContactUsListSerializer
from aparnik.contrib.users.models import User
from aparnik.contrib.contactus.models import *
from aparnik.contrib.messaging.utils import notify
from aparnik.utils.utils import get_request


@shared_task
def send_contact_us_message(contact_us_id):
    """Send chat message create notification and etc via a channel to celery."""
    time.sleep(0.2)
    contact_us = ContactUs.objects.get(pk=contact_us_id)
    serializer = ContactUsListSerializer(contact_us, many=False, read_only=True, context={'request': get_request()})
    users = User.objects.admins()
    for user in users:
        notify(
            uri=contact_us.phone,
            source=User.objects.first(),
            source_display_name=contact_us.fullname,
            recipient=user,
            action='Create',
            obj=contact_us,
            short_description='You a new contact request',
            extra_data={
                'uri': contact_us.phone,
                'message': serializer.data,
            },
            channels=['push'],
            silent=True,
        )
