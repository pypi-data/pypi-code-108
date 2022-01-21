from django.core.management import BaseCommand
from django.conf import settings as django_settings
from django.db import transaction
from askbot import models
import sys

class Command(BaseCommand):

    def handle(self, **options):
        user = models.User.objects.get(id=2)
        for i in range(1000):
            name = 'tag' + str(i)
            models.Tag.objects.create(
                                name=name,
                                created_by=user,
                                language_code=django_settings.LANGUAGE_CODE
                            )
            if i % 1000 == 0:
                transaction.commit()
