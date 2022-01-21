"""Recounts user's badges"""
from askbot import const
from askbot.models import User
from askbot.utils.console import ProgressBar
from django.conf import settings as django_settings
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import translation

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        translation.activate(django_settings.LANGUAGE_CODE)
        users = User.objects.all()
        count = users.count()
        msg = 'Counting user badges'
        for user in ProgressBar(users.iterator(), count, msg):
            user.recount_badges()
            transaction.commit()
