# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import os
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YScoverageConfig(YSAppConfig):
    name = 'yscoverage'
    """str: Python module name (mandatory)."""

    url_prefix = 'coverage'
    """str: Prefix under which to include this module's URLs."""

    verbose_name = 'Various utilities used for analysis of YANG models.'
    """str: Human-readable application name."""

    menus = {
        'Analytics': [
            ('Datasets and diffs', 'datasets'),
        ],
    }
    """dict: Menu items ``{'menu': [(text, relative_url), ...], ...}``"""
    help_pages = [
        ("YANG model coverage", "index.html"),
    ]

    def __init__(self, *args, **kwargs):
        if os.getenv('DJANGO_SETTINGS_MODULE', '') in [
            'yangsuite.settings.dev.develop',
            'yangsuite.settings.develop'
        ]:
            self.menus['Analytics'].append(('YANG coverage', 'coverage'))
        super().__init__(*args, **kwargs)
