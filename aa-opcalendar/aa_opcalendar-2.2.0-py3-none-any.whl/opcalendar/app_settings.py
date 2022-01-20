from django.conf import settings
from .utils import clean_setting
import re


def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0]  # first match

    return url


# Hard timeout for tasks in seconds to reduce task accumulation during outages
OPCALENDAR_TASKS_TIME_LIMIT = clean_setting("OPCALENDAR_TASKS_TIME_LIMIT", 7200)

# whether admins will get notifications about import events
OPCALENDAR_ADMIN_NOTIFICATIONS_ENABLED = clean_setting(
    "OPCALENDAR_ADMIN_NOTIFICATIONS_ENABLED", True
)

# whether we should send out discord notifications for imported fleets
OPCALENDAR_NOTIFY_IMPORTS = clean_setting("OPCALENDAR_NOTIFY_IMPORTS", True)

# whether we should inculde timers from the structuretimers plugin in the calendar
OPCALENDAR_DISPLAY_STRUCTURETIMERS = clean_setting(
    "OPCALENDAR_DISPLAY_STRUCTURETIMERS", True
)

# whether we should inculde extractions from the moonmining plugin in the calendar
OPCALENDAR_DISPLAY_MOONMINING = clean_setting("OPCALENDAR_DISPLAY_MOONMINING", True)

# whether we display external hosts in the discord ops command filters
OPCALENDAR_DISCORD_OPS_DISPLAY_EXTERNAL = clean_setting(
    "OPCALENDAR_DISCORD_OPS_DISPLAY_EXTERNAL", False
)

OPCALENDAR_EVE_UNI_URL = "https://portal.eveuniversity.org/api/getcalendar"
OPCALENDAR_SPECTRE_URL = "https://www.spectre-fleet.space/engagement/events/rss"
OPCALENDAR_FUNINC_URL = "https://calendar.google.com/calendar/ical/og3uh76l8ul3dfgbie03fbbgs8%40group.calendar.google.com/private-f466889b44741fd7249e99e21ac171ff/basic.ics"
OPCALENDAR_FRIDAY_YARRRR_URL = "https://calendar.google.com/calendar/ical/vl43scrg7olk01fv7g79hsbe74%40group.calendar.google.com/public/basic.ics"
OPCALENDAR_REDEMPTION_ROAD_URL = "https://calendar.google.com/calendar/ical/5o3gpum6ek2irk12f0hnhfdtrs%40group.calendar.google.com/public/basic.ics"
OPCALENDAR_CAS_URL = "https://calendar.google.com/calendar/ical/0sqru3js6pb1p71e7n1ko91rqs%40group.calendar.google.com/public/basic.ics"
OPCALENDAR_FWAMING_DWAGONS_URL = "https://calendar.google.com/calendar/ical/l0mnjo7ormaq9gomap0cke4kqk%40group.calendar.google.com/public/basic.ics"
OPCALENDAR_FREE_RANGE_CHIKUNS_URL = "https://calendar.google.com/calendar/ical/2nabdlgsebhsv29qmhtjgd0u9k%40group.calendar.google.com/public/basic.ics"
OPCALENDAR_EVE_LINKNET_URL = "https://auth.eve-linknet.com/opcalendar/feed.ics"


def structuretimers_active():
    return "structuretimers" in settings.INSTALLED_APPS


def moonmining_active():
    return "moonmining" in settings.INSTALLED_APPS


# Use a small helper to check if AA-Discordbot is installs
def discord_bot_active():
    return "aadiscordbot" in settings.INSTALLED_APPS
