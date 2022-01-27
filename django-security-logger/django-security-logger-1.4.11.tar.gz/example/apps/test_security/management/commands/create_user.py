from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from reversion.revisions import create_revision


class Command(BaseCommand):

    @create_revision()
    def handle(self, **options):
        User.objects._create_user('test', 'test@localhost', 'test', is_staff=True, is_superuser=True)
