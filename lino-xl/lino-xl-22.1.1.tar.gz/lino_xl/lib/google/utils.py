import json
import requests
import datetime
import logging; logger = logging.getLogger(__name__)
from pathlib import Path
from dateutil.parser import parse

try:
    from google.oauth2.credentials import Credentials
    from google.auth.exceptions import RefreshError
    from googleapiclient._auth import is_valid, refresh_credentials
    from googleapiclient.discovery import build
except ImportError:
    pass

from django.utils import timezone
from lino.core.site import has_socialauth

from lino.api import dd


def get_credentials(me):

    with open(dd.plugins.google.client_secret_file) as f:
        client_secret = json.load(f)

    if type(me.extra_data['scopes']) == str:
        me.extra_data['scopes'] = me.extra_data['scopes'].split()

    def get_expiry(creds):
        from_auth_time_and_delta = datetime.datetime.fromtimestamp(
            creds['auth_time']) + datetime.timedelta(seconds=creds['expires_in'])
        if creds['expiry']:
            return max(datetime.datetime.fromtimestamp(creds['expiry']),
                        from_auth_time_and_delta)
        return from_auth_time_and_delta

    creds = Credentials(
        token_uri=client_secret['web']['token_uri'],
        client_id=client_secret['web']['client_id'],
        client_secret=client_secret['web']['client_secret'],
        token=me.extra_data['access_token'],
        refresh_token=me.extra_data['refresh_token'],
        rapt_token=me.extra_data['rapt_token'],
        id_token=me.extra_data['id_token'],
        expiry=get_expiry(me.extra_data),
        scopes=me.extra_data['scopes']
    )

    if not is_valid(creds):
        try:
            refresh_credentials(creds)
            me.extra_data['access_token'] = creds.token
            me.extra_data['expiry'] = datetime.datetime.timestamp(creds.expiry)
            me.extra_data['refresh_token'] = creds.refresh_token
            me.extra_data['rapt_token'] = creds.rapt_token
            me.full_clean()
            me.save()
        except RefreshError as e:
            requests.post('https://oauth2.googleapis.com/revoke',
                params={'token': creds.token},
                headers={'content-type': 'application/x-www-form-urlencoded'})
            logger(f"{me.user}'s Token has been revoked, because of this:\n{e}\nNeeds re-authentication.")
            me.delete()

    return creds

def get_resource(user):
    from social_django.models import UserSocialAuth
    social_user = UserSocialAuth.objects.get(user=user, provider='google')
    creds = get_credentials(social_user)
    return build('calendar', 'v3', credentials=creds)

def map_calendar_into_dbModel(cls, cal):
    calendar, _ = cls.objects.get_or_create(google_id=cal.get('id'))
    calendar.name=cal.get('summary')
    calendar.description=cal.get('description')
    calendar.time_zone=cal.get('timeZone')
    return calendar

def map_event_into_dbModel(cls, event, user_s_cal):
    e = cls.objects.get_or_create(
        google_id=event['id'], google_calendar=user_s_cal.calendar)
    e.status = event.get('status') # possible values are 'confirmed', 'tentative', 'cancelled'
    e.summary = event.get('summary') # The title of the event
    e.description = event.get('description')
    e.sequence = event.get('sequence')

    def resolve_datetime(stamp):
        if hasattr(stamp, 'timeZone'):
            with timezone.override(stamp['timeZone']):
                dt = parse(stamp['dateTime']).replace(
                    tzinfo=timezone.get_current_timezone())
            dt = timezone.make_naive(dt)
        else:
            dt = timezone.make_naive(parse(stamp['dateTime']))
        return dt.date(), dt.time()

    if hasattr(event, 'start'):
        if hasattr(event['start'], 'dateTime'):
            e.start_date, e.start_time = resolve_datetime(event['start'])
        else:
            e.start_date = datetime.date(
                *map(int, event['start']['date'].split('-')))

    if hasattr(event, 'end'):
        if hasattr(event['end'], 'dateTime'):
            e.end_date, e.end_time = resolve_datetime(event['end'])
        else:
            e.end_date = datetime.date(
                *map(int, event['end']['date'].split('-')))

    e.location = event.get('location')
    pass
