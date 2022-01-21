# -*- coding: utf-8 -*-



from django.db import models, migrations
from django.db.models import Sum
from django.utils import translation
from django.utils.translation import ugettext as _
from askbot.utils.console import ProgressBar
from askbot import const

def populate_language_in_reps(apps, schema_editor):
    Repute = apps.get_model('askbot', 'Repute')
    reputes = Repute.objects
    message = 'Applying language to the reputation records'
    print('')
    for rep in ProgressBar(reputes.iterator(), reputes.count(), message):
        if rep.question_id:
            lang = rep.question.language_code
        else:
            lang = rep.user.askbot_profile.primary_language
        rep.language_code = lang
        rep.save()


def calculate_localized_reps(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('askbot', 'LocalizedUserProfile')
    Repute = apps.get_model('askbot', 'Repute')

    users = User.objects
    message = 'Calculating localized reputations'
    print('')
    for user in ProgressBar(users.iterator(), users.count(), message):
        reps = user.repute_set.values('language_code')
        reps = reps.annotate(
                            negative=Sum('negative'),
                            positive=Sum('positive')
                        )

        for rep in reps:
            lang = rep['language_code']
            profile, junk = Profile.objects.get_or_create(
                                                    auth_user=user,
                                                    language_code=lang)
            profile.reputation = max(0, rep['positive'] + rep['negative'])
            profile.save()

        #recalculate the total reputation
        aggregate = Profile.objects.filter(
                                    auth_user=user
                                ).aggregate(reputation=Sum('reputation'))

        aggregate_rep = aggregate['reputation'] or 0 #dict might have 'None' value
        new_rep = const.MIN_REPUTATION + aggregate_rep
        old_rep = user.askbot_profile.reputation

        #compensate if new rep is less than old
        if new_rep < old_rep:
            comp = Repute()
            comp.user = user
            comp.positive = old_rep - new_rep
            comp.reputation_type = 10
            with translation.override(user.askbot_profile.primary_language):
                comp.comment = _('Compensated by admin during recalculation of karma')
            comp.save()
            new_rep = old_rep

        #update total reputation
        if new_rep != old_rep:
            user.askbot_profile.reputation = new_rep
            user.askbot_profile.save()
            print('old %d new %d' % (old_rep, new_rep))


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0009_auto_20160103_1150'),
    ]

    operations = [
        migrations.RunPython(populate_language_in_reps),
        migrations.RunPython(calculate_localized_reps)
    ]
