
import datetime, time

from django.db import models

from lino.modlib.users.mixins import UserAuthored
from lino_xl.lib.cal.models import Calendar, BaseSubscription, Event
from lino.api import dd, _

from .utils import get_resource, map_calendar_into_dbModel, map_event_into_dbModel

class UserSubscriptionToCalendar(BaseSubscription):
    user_access_role = dd.CharField(max_length=20, default='reader')
    event_sync_token = dd.CharField(max_length=200, blank=True)
    """Used to retrive only the changed entries from the remote server."""

class CalendarListToken(UserAuthored):
    allow_cascaded_delete = ['user']
    sync_token = dd.CharField(max_length=200, blank=True)
    """Used to retrive only the changed entries from the remote server."""


def sync_calendar_events(resource, user_s_cal):
    def sync10(nextPageToken=None):
        events_list = resource.events().list(
            calendarId=user_s_cal.calendar.google_id, maxResults=10,
            syncToken=user_s_cal.event_sync_token, pageToken=nextPageToken).execute()
        user_s_cal.event_sync_token = events_list.get('nextSyncToken')

        for event in events_list['items']:
            map_event_into_dbModel(Event, event, user_s_cal)

        next_page_token = events_list.get('nextPageToken')
        if next_page_token:
            sync10(next_page_token)
    sync10()
    user_s_cal.full_clean()
    user_s_cal.save()


def sync_user_calendar(user):
    gcal = get_resource(user)

    cl_token, _ = CalendarListToken.objects.get_or_create(user=user)

    def sync10(nextPageToken=None):
        cal_list = gcal.calendarList().list(max_results=10, syncToken=cl_token.sync_token, pageToken=nextPageToken).execute()
        cl_token.sync_token = cal_list.get('nextSyncToken')

        for cal in cal_list['items']:
            calendar = map_calendar_into_dbModel(Calendar, cal)
            calendar.full_clean()
            calendar.save()

            user_s_cal, _ = UserSubscriptionToCalendar.objects.get_or_create(
                calendar=calendar, user=user)
            user_s_cal.is_hidden = cal.get('hidden')
            user_s_cal.user_access_role=cal.get('accessRole')

            sync_calendar_events(gcal, user_s_cal)

        next_page_token = cal_list.get('nextPageToken')
        if next_page_token:
            sync10(next_page_token)
    sync10()
    cl_token.full_clean()
    cl_token.save()


class SynchronizeGoogle(dd.Action):
    help_text = _("Synchronize this database row with Google.")
    label = _("Sync Google Calendar")
    select_rows = False

    def run_from_ui(self, ar):
        sync_user_calendar(ar)
        ar.success()

dd.inject_action('users.User', synchronize_google=SynchronizeGoogle())
