from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import VimeoSettings, api_list, api_single

urlpatterns = [
    re_path(
        fr"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/vimeo/$",
        VimeoSettings.as_view(),
        name="settings",
    ),
    re_path(
        fr"^api/events/(?P<event>[{SLUG_CHARS}]+)/p/vimeo/$",
        api_list,
        name="api_list",
    ),
    re_path(
        fr"^api/events/(?P<event>[{SLUG_CHARS}]+)/submissions/(?P<code>[A-Z0-9]+)/p/vimeo/$",
        api_single,
        name="api_single",
    ),
]
