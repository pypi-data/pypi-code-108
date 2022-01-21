"""Management commands alerting of content on the moderation queue"""
from django.core.management import BaseCommand
from django.conf import settings as django_settings
from django.utils import translation
from askbot import const
from askbot.mail.messages import ModerationQueueNotification
from askbot.models import Activity
from askbot.models import User, get_users_by_role
from askbot.models.user import get_invited_moderators

def get_last_mod_alert_activity():
    """return latest moderation alert activity"""
    atype = const.TYPE_ACTIVITY_MODERATION_ALERT_SENT
    acts = Activity.objects.filter(activity_type=atype).order_by('-id')
    count = len(acts)
    if count == 0:
        return None
    last_act = acts[0]

    if count > 1:
        #get last moderation activity and delete all others
        acts = acts.exclude(id=last_act.id)
        acts.delete()

    return last_act


def get_last_notified_user():
    """Get user that was modified last about the queue"""
    last_act = get_last_mod_alert_activity()
    if last_act:
        return last_act.content_object
    return None


def select_moderators_to_notify(candidates, num_needed):
    """Selects some nomber of moderators to send the message,
    in order to avoid spamming many people"""
    candidates_count = candidates.count()

    #special case - if we need to notify the same number of
    #moderators that are available, then we don't rotate them
    #and notify all, b/c otherwise we would stop notifications
    #because there are not enough moderators
    if candidates_count <= num_needed:
        return list(candidates)

    last_notified = get_last_notified_user()
    if last_notified is None:
        return candidates[:num_needed]

    mods = list(candidates.filter(id__gt=last_notified.id))
    num_mods = len(mods)
    if num_mods >= num_needed:
        return mods[:num_needed]

    #wrap around the end to the beginning
    num_missing = num_needed - num_mods
    more_mods = get_users_by_role('recv_mod_alerts').order_by('id')
    more_mods = more_mods[:num_missing]
    mods.extend(list(more_mods))
    return mods


def select_last_moderator(mods):
    """Returns object with the largest .id value."""
    return max(mods, key=lambda item: item.id)


def remember_last_moderator(user):
    """Save the the `user` as the one that was notified last"""
    act = get_last_mod_alert_activity()
    if act:
        act.content_object = user
        act.save()
    else:
        act = Activity(
            user=user,
            content_object=user,
            activity_type=const.TYPE_ACTIVITY_MODERATION_ALERT_SENT
        )
        act.save()


class Command(BaseCommand):
    """The management command class"""
    def handle(self, **options): #pylint: disable=unused-argument
        """Function that does the job of the management command"""
        #get size of moderation queue
        translation.activate(django_settings.LANGUAGE_CODE)
        act_types = const.MODERATED_ACTIVITY_TYPES
        queue = Activity.objects.filter(activity_type__in=act_types)

        if queue.count() == 0:
            return

        #get moderators
        mods = get_users_by_role('recv_mod_alerts').order_by('id')
        mods = select_moderators_to_notify(mods, 3) #todo: add setting
        mods = set(mods)
        all_mods = mods | get_invited_moderators()

        if not all_mods:
            return

        for mod in all_mods:
            email = ModerationQueueNotification({'user': mod})
            email.send([mod,])

        if not mods:
            return

        last_mod = select_last_moderator(mods)
        remember_last_moderator(last_mod)
