"""Replaces django-avatar 'rebuild_avatars'
and saves cached active avatar urls for each user"""
from askbot.models import User, UserProfile
from askbot.utils.console import ProgressBar
from avatar.conf import settings as avatar_settings
from avatar.models import Avatar
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        avatars = Avatar.objects.all()
        count = avatars.count()
        message = 'Rebuilding avatar thumbnails'
        for avatar in ProgressBar(avatars.iterator(), count, message):
            for size in avatar_settings.AVATAR_AUTO_GENERATE_SIZES:
                avatar.create_thumbnail(size)

        users = User.objects.all()
        count = users.count()
        message = 'Rebuilding cached avatar urls'
        for user in ProgressBar(users.iterator(), count, message):
            user.init_avatar_urls()
            UserProfile.objects.filter(auth_user_ptr=user).update(avatar_urls=user.avatar_urls)
            profile = UserProfile.objects.get(pk=user.pk)
            profile.update_cache()
