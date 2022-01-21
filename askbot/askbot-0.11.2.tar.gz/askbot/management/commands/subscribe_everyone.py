
from django.core.management import BaseCommand
from django.db import connection
from askbot.models import EmailFeedSetting, User

class Command(BaseCommand):
    def handle(self, **options):
        try:
            try:
                self.subscribe_everyone()
            except Exception as e:
                print(e)
        finally:
            connection.close()

    def subscribe_everyone(self):

        for user in User.objects.all():
            for feed_type in EmailFeedSetting.FEED_TYPES:
                feed_setting, created = EmailFeedSetting.objects.get_or_create(
                                                subscriber=user,
                                                feed_type = feed_type[0]
                                            )
                feed_setting.frequency = 'w'
                feed_setting.reported_at = None
                feed_setting.save()
