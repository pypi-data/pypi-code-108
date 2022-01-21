from django.conf import settings as django_settings
from django.core.management import BaseCommand
from django.db.models import Count
from django.db import transaction
from django.utils import translation
from askbot.models import User
from askbot import forms

class Command(BaseCommand):
    def handle(self, **options):
        translation.activate(django_settings.LANGUAGE_CODE)
        for user in User.objects.all().iterator():
            user.add_missing_askbot_subscriptions()
            transaction.commit()
