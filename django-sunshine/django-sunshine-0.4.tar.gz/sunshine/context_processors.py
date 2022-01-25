# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from django.conf import settings
from .apps import is_developer
from .common import read_settings, build_menu


SUNSHINE_ADMIN_GROUPS = getattr(settings, 'SUNSHINE_ADMIN_GROUPS', [])
TIME_ZONE_DST = settings.TIME_ZONE_DST
DEBUG = settings.DEBUG
SUNSHINE_ENV = read_settings('SUNSHINE_ENV', 'DEV')
SUNSHINE_BRAND = read_settings('SUNSHINE_BRAND', f"{SUNSHINE_ENV} Sunshine <sup>2</sup>")
DEFAULT_LOGO = 'sunshine/images/local.png'
SUNSHINE_DEFAULT_TITLE = read_settings('SUNSHINE_DEFAULT_TITLE', 'Sunshine Portal')
LOGO_MAP = {
    'DEV': 'sunshine/images/local.png',
    'UAT': 'sunshine/images/uat.png',
    'PROD': 'sunshine/images/prod.png'
}
SUNSHINE_ADMIN_LOGO = read_settings('SUNSHINE_ADMIN_LOGO',
                                    LOGO_MAP[SUNSHINE_ENV] if SUNSHINE_ENV in LOGO_MAP else DEFAULT_LOGO)

COPYRIGHT_FOOTER = read_settings(
    "SUNSHINE_COPYRIGHT",
    """Sunshine Portal, &copy; <a target='_blank' href='https://github.com/letuananh/sunshine'>Le Tuan Anh</a>, 2013""")


def username(request):
    ''' Get current user's login account name '''
    if request.user.is_authenticated:
        # try to user fullname first ...
        username = "{} {}".format(request.user.first_name, request.user.last_name).strip()
        if not username:
            username = request.user.username
    else:
        username = 'Anonymous'
    return username


def setup_sunshine_request(request):
    menu = build_menu(request)
    return {
        # sunshine site configuration
        'SUNSHINE_BRAND': SUNSHINE_BRAND,
        'SUNSHINE_ADMIN_LOGO': SUNSHINE_ADMIN_LOGO,
        'SUNSHINE_COPYRIGHT': COPYRIGHT_FOOTER,
        'SUNSHINE_ENV': SUNSHINE_ENV,
        'DEBUG': DEBUG,
        'SUNSHINE_DEFAULT_TITLE': SUNSHINE_DEFAULT_TITLE,
        # sunshine menu
        'sunshine_main_menu': menu,
        # user related info
        'username': username(request),
        'access_dev': is_developer(request.user),
        'sidebar_toggle': request.session.get('sidebar_toggle', True)
    }
