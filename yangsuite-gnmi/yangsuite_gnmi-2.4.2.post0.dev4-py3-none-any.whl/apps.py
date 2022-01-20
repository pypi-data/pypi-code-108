try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSgNMIConfig(YSAppConfig):
    name = 'ysgnmi'
    """str: Python module name (mandatory)."""

    url_prefix = 'gnmi'
    """str: Prefix under which to include this module's URLs."""

    verbose_name = ('gRPC Network Management Interface (gNMI) support'
                    ' for YANG Suite')
    """str: Human-readable application name."""

    menus = {
        'Protocols': [
            ('gNMI', 'explore'),
        ],
    }
    """dict: Menu items ``{'menu': [(text, relative_url), ...], ...}``"""

    help_pages = [
        ('yangsuite-gnmi documentation', 'index.html')
    ]
    """list: of tuples ``('title', 'file path')``.

    The path is relative to the directory ``<app>/static/<app>/docs/``.
    """
