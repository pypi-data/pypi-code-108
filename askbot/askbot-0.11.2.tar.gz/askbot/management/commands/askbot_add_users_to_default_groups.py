from django.core.management import BaseCommand
from askbot.models import User
from askbot.utils.console import ProgressBar

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        users = User.objects.all()
        count = users.count()
        message = 'Adding users to global and personal groups'
        for user in ProgressBar(users.iterator(), count, message):
            user.join_default_groups()
