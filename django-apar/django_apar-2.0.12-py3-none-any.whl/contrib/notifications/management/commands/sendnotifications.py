# -*- coding: utf-8 -*-


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


class Command(BaseCommand):
    # Show this when the user types help
    help = "send notification"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        finished_time = now()

        print(('send notifications %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
