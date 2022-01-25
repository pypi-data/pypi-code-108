# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from django.apps import AppConfig
from django.conf import settings

SUNSHINE_ADMIN_GROUPS = getattr(settings, 'SUNSHINE_ADMIN_GROUPS', [])


def is_developer(user):
    return user.is_superuser or \
        (SUNSHINE_ADMIN_GROUPS and
         user.groups.filter(name__in=SUNSHINE_ADMIN_GROUPS).exists()
         )


class SunshinePortalConfig(AppConfig):
    name = 'sunshine'
    verbose_name = 'Sunshine Portal'
    sunshine_menu = [
        {'title': 'System Dashboard',
         'name': 'system_dashboard',
         'verify': lambda req: is_developer(req.user),
         'groups': ['Developer']
         },
        {'name': 'admin:index',
         'verify': lambda req: is_developer(req.user),
         'title': 'Django Admin',
         'icon': 'fa-tools',
         'groups': ['Developer']}
    ]
