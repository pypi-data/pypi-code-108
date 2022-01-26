from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from reversion.revisions import create_revision


class Command(BaseCommand):

    def handle(self, **options):
        for i in range(100):
            with create_revision():
                User.objects._create_user(
                    f'test{i}', f'test{i}@localhost', f'test{i}', is_staff=True, is_superuser=True
                )
