# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from lino_xl.lib.google.utils import get_service
#
# SCOPES = [
#     'https://www.googleapis.com/auth/calendar',
#     'https://www.googleapis.com/auth/calendar.events'
# ]
#
# service = get_service('calendar', 'v3', SCOPES)
#
# def get_events():
#     now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#     events_result = service.events().list(calendarId='primary', timeMin=now,
#                                         maxResults=10, singleEvents=True,
#                                         orderBy='startTime').execute()
#     events = events_result.get('items', [])
#
#     if not events:
#         return None
#     result = dict()
#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         result.update(start=start, event_summary=event['summary'])
#     return result
