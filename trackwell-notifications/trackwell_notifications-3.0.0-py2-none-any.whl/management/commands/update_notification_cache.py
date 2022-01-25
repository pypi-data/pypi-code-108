# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from accounts.models import UserNotification


class Command(BaseCommand):
    help = 'Updates cache entries for notifications'

    def handle(self, *args, **options):
        print('update_unseen_notification_cache')
        unseen = UserNotification.objects.all()
        for un in unseen:
            un.update_unseen_cache()
        print('Cache entries for {} notifications updated'.format(unseen.count()))
