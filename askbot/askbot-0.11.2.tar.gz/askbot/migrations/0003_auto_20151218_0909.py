# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings as django_settings
from askbot.utils.console import ProgressBar


def get_primary_language(profile):
    langs = profile.languages.strip().split()
    if langs:
        return langs[0]
    return django_settings.LANGUAGE_CODE


def populate_localized_user_profiles(apps, schema_editor):
    UserProfile = apps.get_model('askbot', 'UserProfile')
    LocalizedUserProfile = apps.get_model('askbot', 'LocalizedUserProfile')
    profiles = UserProfile.objects.all()
    message = 'creating localized user profiles, and copying "about" field'
    for profile in ProgressBar(profiles.iterator(), profiles.count(), message):
        loc_profile = LocalizedUserProfile()
        loc_profile.auth_user = profile.auth_user_ptr
        loc_profile.language_code = get_primary_language(profile)
        loc_profile.about = profile.about
        loc_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0002_auto_20151218_0908'),
    ]

    operations = [
        migrations.RunPython(populate_localized_user_profiles),
    ]
