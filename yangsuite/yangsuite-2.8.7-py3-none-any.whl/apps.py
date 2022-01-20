# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

import os
from django.apps import AppConfig
import django.utils.autoreload
from yangsuite.paths import get_base_path

FAILED_APPS = {}
"""Dict of app: failure message"""


CANARY_FILE = None
"""File that will trigger Django process restart if touched.

Value is assigned in _YangsuiteConfig.ready() method."""


class YSAppConfig(AppConfig):
    """Extension of :class:`AppConfig` for YANG Suite applications.

    Plugins / applications that wish to support autodiscovery by YANG Suite
    must create a subclass of this class and register their class via their
    ``setup.py`` as an ``entry_points`` item under group ``[yangsuite.apps]``.
    """

    # Base AppConfig parameters that are mandatory:

    name = None
    """str: Full Python path to the app, e.g. 'yangsuite', 'ysdevices'."""

    verbose_name = None
    """str: Paragraph-length description of this application or plugin."""

    # Additional optional parameters for YANG Suite applications

    url_prefix = None
    """str: Preferred prefix regexp under which to add app's urlpatterns."""

    menus = None
    """dict: ``{'menu title': [('menu item', 'relative url'), ...], ...}``.

    To add a separator to a menu, use ``('--', None)`` as an item.
    """

    help_pages = None
    """list: of tuples ``(title, pagename)``.

    Each listed page should be found in ``<app>/static/<app>/docs`` directory.

    In YANG Suite's online help system, the table of contents for this
    application will list the help files in the order specified in this list.
    If you don't set this list, the help files will be listed in alphabetical
    order, which may not be ideal.
    """


class _YangsuiteConfig(YSAppConfig):
    """The configuration for yangsuite itself."""
    name = 'yangsuite'
    url_prefix = ''
    verbose_name = (
        "Core application logic for YANG Suite."
        " Capable of dynamic discovery of installed application plugins."
        " Provides common library APIs for logging, filesystem access,"
        " GUI appearance and behavior, and client-server communication."
    )

    # Provide basic menu scaffolding plus core menu items
    menus = {
        'Admin': [
            ('Manage users', 'admin'),
            ('Manage plugins', 'yangsuite/plugins/'),
            ('View logs', 'yangsuite/logs'),
        ],
        'Setup': [],
    }

    help_pages = [
        ('Getting started with YANG Suite', 'introduction.html')
    ]

    def ready(self):
        import yangsuite.signals   # noqa: F401

        # Create a canary file that we can touch to trigger a Django restart.
        # https://stackoverflow.com/questions/42907285
        #
        # Note that this is using undocumented Django APIs, and *will* break
        # when we migrate to Django 2.1 due to major refactoring of these APIs:
        # https://github.com/django/django/pull/8819
        #
        # Note also that this will only work if Django is running in
        # development mode and the '--noreload' option was not passed.
        # In production deployment, or on Windows (where we use --noreload
        # by necessity), the server will need to be manually restarted.
        global CANARY_FILE
        CANARY_FILE = os.path.join(get_base_path(), 'yangsuite.canary')
        if not os.path.exists(CANARY_FILE):
            with open(CANARY_FILE, 'w'):
                pass
        django.utils.autoreload._cached_filenames.append(CANARY_FILE)
