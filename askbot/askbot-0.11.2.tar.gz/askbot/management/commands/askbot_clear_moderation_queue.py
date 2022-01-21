from django.core.management import BaseCommand
from askbot import const
from askbot.models import Activity

ACTIVITY_TYPES = (
    const.TYPE_ACTIVITY_MODERATED_NEW_POST,
    const.TYPE_ACTIVITY_MODERATED_POST_EDIT,
    const.TYPE_ACTIVITY_MARK_OFFENSIVE
)

class Command(BaseCommand):
    help = 'deletes all items from the moderation queue'
    def handle(self, *args, **kwargs):
        acts = Activity.objects.filter(activity_type__in=ACTIVITY_TYPES)
        acts.delete()
