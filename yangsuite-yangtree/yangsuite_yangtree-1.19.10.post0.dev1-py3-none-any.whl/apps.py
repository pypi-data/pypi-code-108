# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSYangTreeConfig(YSAppConfig):
    name = 'ysyangtree'
    """Python module name/path"""

    verbose_name = (
        "Manages loading, caching, and validation of YANG "
        '(<a href="https://tools.ietf.org/html/rfc6020">RFC 6020</a>, '
        '<a href="https://tools.ietf.org/html/rfc7950">RFC 7950</a>) models. '
        "Represents parsed YANG models as Python dicts and JavaScript trees. "
        "Adds GUI for traversing, searching, and inspecting YANG model trees."
    )
    """More human-readable name"""

    url_prefix = 'yangtree'
    """Prefix under which to include this app's urlpatterns."""

    # Menu items {'menu': [(text, relative_url), ...], ...}
    menus = {
        'Explore': [
            ('YANG', 'explore'),
        ],
    }

    help_pages = [
        ('Exploring YANG', 'index.html'),
    ]
