# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSDevicesConfig(YSAppConfig):
    # Python module name (mandatory)
    name = 'ysdevices'

    # Prefix under which to include this module's URLs
    url_prefix = 'devices'

    # Human-readable label
    verbose_name = (
        "Provides common infrastructure for definition and management of"
        " network device profiles. Manages device profile validation"
        " in the form of connectivity and credential checks."
    )

    # Menu items {'menu': [(text, relative_url), ...], ...}
    menus = {
        'Setup': [
            ('Device profiles', 'devprofile'),
        ],
    }

    help_pages = [
        ("Defining a device profile", "index.html"),
    ]
