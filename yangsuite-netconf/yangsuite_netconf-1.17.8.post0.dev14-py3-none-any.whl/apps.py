# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSNetconfConfig(YSAppConfig):
    # Python module name (mandatory)
    name = 'ysnetconf'

    # Prefix under which to include this module's URLs
    url_prefix = 'netconf'

    # Detailed user-facing string
    verbose_name = (
        'Adds NETCONF protocol'
        ' (<a href="https://tools.ietf.org/html/rfc6241">RFC 6241</a>,'
        ' <a href="https://tools.ietf.org/html/rfc7950">RFC 7950</a>)'
        ' support to YANG Suite. Allows the user to build NETCONF RPC messages'
        ' and execute them on live network devices that support NETCONF.'
        ' Users can also subscribe to NETCONF event notifications'
        ' (<a href="https://tools.ietf.org/html/rfc5277">RFC 5277</a>)'
        ' from devices with this capability.'
    )

    # Menu items {'menu': [(text, relative_url), ...], ...}
    menus = {
        'Protocols': [
            ('NETCONF', 'getyang'),
        ],
    }

    help_pages = [
        ('Using NETCONF RPCs', 'rpcs.html'),
        ('Working with NETCONF notifications', 'notifications.html'),
        ('Using replays for repeated workflows', 'tasks.html'),
        ('Locking and unlocking datastores', 'lock-unlock.html'),
    ]
