# -*- coding: utf-8 -*-


from askbot.utils.console import ProgressBar
from django.db import models, migrations
from django.conf import settings as django_settings


DROP_QUERY = 'DROP TRIGGER IF EXISTS auth_user_tsv_update_trigger ON auth_user;'
def drop_user_profile_trigger(app, schema_editor):
    conn = schema_editor.connection
    if hasattr(conn, 'vendor') and conn.vendor == 'postgresql':
        cursor = conn.cursor()
        cursor.execute(DROP_QUERY)


def get_primary_language(profile):
    langs = profile.languages.strip().split()
    if langs:
        return langs[0]
    return django_settings.LANGUAGE_CODE


def populate_primary_language(apps, schema_editor):
    Profile = apps.get_model('askbot', 'UserProfile')
    profiles = Profile.objects.all()
    message = 'Populating primary language field'
    for profile in ProgressBar(profiles.iterator(), profiles.count(), message):
        profile.primary_language = get_primary_language(profile)
        profile.save()


def populate_claimed_localized_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('askbot', 'UserProfile')
    users = User.objects.all()
    message = 'Marking claimed localized user profiles'
    for user in ProgressBar(users.iterator(), users.count(), message):
        profile, junk = Profile.objects.get_or_create(pk=user.pk)
        langs = profile.languages.strip().split()
        localized_profiles = user.localized_askbot_profiles.all()
        for localized in localized_profiles:
            if localized.language_code in langs:
                localized.is_claimed = True
                localized.save()


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0005_auto_20151220_0450'),
    ]

    operations = [
        migrations.RunPython(drop_user_profile_trigger),
        migrations.RunPython(populate_primary_language),
        migrations.RunPython(populate_claimed_localized_profiles)
    ]
