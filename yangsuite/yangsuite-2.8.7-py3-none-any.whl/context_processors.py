# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# -*- coding: utf-8 -*-

r"""Django context processors for YANG Suite.

These are used to inject implicit parameters into Django templates, if
enabled in the project settings file.

.. seealso:: https://docs.djangoproject.com/en/1.10/ref/templates/api/

The processors currently available are:

- :func:`yangsuite.context_processors.yangsuite_menus`
    Provides the dynamically built dictionary used to construct
    the drop-down menus at the top of every YANG Suite web page.
"""
from __future__ import unicode_literals

from collections import namedtuple, OrderedDict

from django.apps import apps

from yangsuite.apps import YSAppConfig
from yangsuite.logs import get_logger

log = get_logger(__name__)


def yangsuite_menus(request):
    """Populate the 'yangsuite_menus' template parameter.

    Enabled in settings.py as ``yangsuite.context_processors.yangsuite_menus``.

    Returns:
      dict: with key ``yangsuite_menus``.
    """
    return {
        'yangsuite_menus': build_yangsuite_menus(),
    }


YSMenuItem = namedtuple('YSMenuItem', ['text', 'url'])
"""Named tuple describing a menu item with display text and a link url."""


_yangsuite_menus = OrderedDict()
"""Dict of lists of YSMenuItems returned by :func:`yangsuite_menus`."""


def build_yangsuite_menus():
    """Build the yangsuite_menus dict if not already built.

    Ensures that the first three menus are "Admin", "Setup", and "Operations";
    any additional menus will be presented in alphabetical order after this.

    Within the three core menus, core application menu items will be at the
    top of the menu, and all other items will follow.

    Returns:
      collections.OrderedDict: ``{'title': [YSMenuItem, YSMenuItem], ...}``
    """
    global _yangsuite_menus
    if _yangsuite_menus:
        return _yangsuite_menus

    # Core apps are presented in a specific hard-coded order
    core_apps = []
    core_app_names = [
        'yangsuite',
        'ysfilemanager',
        'ysdevices',
        'ysyangtree',
    ]
    for core_app_name in core_app_names:
        try:
            ac = apps.get_app_config(core_app_name)
        except LookupError:
            log.warning('Core app "%s" not found in application registry!',
                        core_app_name)
            # We could add these to apps.FAILED_APPS, but that causes unneeded
            # noise for testing any other app that doesn't actually require
            # all of these apps. So we don't.
            continue
        assert isinstance(ac, YSAppConfig)
        core_apps.append(ac)

    # Non-core apps are sorted to alphabetical order so as to ensure that the
    # order in which they get to add items to the menus (and the resulting
    # order of the items in a menu touched by multiple apps) is stable.
    noncore_apps = []
    for ac in sorted(apps.get_app_configs(), key=lambda ac: ac.label):
        if not isinstance(ac, YSAppConfig):
            continue
        if ac.name in core_app_names:
            continue
        noncore_apps.append(ac)

    # Iterate over installed YANG Suite apps and add their menus if any.
    for ac in core_apps:
        _add_menus_from_app(ac)

    # Add separator to end of core menus before appending non-core items
    for title in _yangsuite_menus.keys():
        if any(title in ac.menus for ac in noncore_apps):
            _register_menu_item(title, '--', None)

    for ac in noncore_apps:
        _add_menus_from_app(ac)

    # Sort to ['Admin', 'Setup', 'Operations', <others alphabetized>]
    # Help item is added explicitly in the page template, not part of this
    def sort_function(kv):
        core_menus = ['Admin', 'Setup', 'Operations']
        if kv[0] in core_menus:
            return (core_menus.index(kv[0]), kv[0])
        else:
            return (10, kv[0])

    _yangsuite_menus = OrderedDict(sorted(_yangsuite_menus.items(),
                                          key=sort_function))

    log.info("yangsuite_menus is now: %s", _yangsuite_menus)
    return _yangsuite_menus


def _add_menus_from_app(ac):
    """Add menu items from the given YSAppConfig."""
    if not ac.menus:
        return

    if ac.url_prefix is None:
        log.error("Not adding menus from app %s because "
                  "it does not define a url_prefix value",
                  ac.name)
        return

    log.debug("Adding menus from %s", ac.name)
    for title, items in ac.menus.items():
        _register_menu(title)
        for text, url in items:
            fullurl = _build_url(ac.url_prefix, url)
            _register_menu_item(title, text, fullurl)


def _build_url(prefix, suffix):
    """Combine the prefix and suffix into an appropriate URL.

    Format will be /prefix/suffix, or if no prefix, /suffix.
    """
    fullurl = '/'
    if prefix.startswith('/'):
        prefix = prefix[1:]
    fullurl += prefix
    if fullurl.endswith('/'):
        if suffix.startswith('/'):
            fullurl = fullurl[:-1]
    elif suffix and not suffix.startswith('/'):
        fullurl += '/'
    fullurl += suffix
    return fullurl


def _register_menu(title):
    """Add a new menu header if not already defined.

    Args:
      title (str): Title string
    """
    global _yangsuite_menus
    if title not in _yangsuite_menus:
        _yangsuite_menus[title] = []
        log.debug("Added menu '%s'; menus are now %s",
                  title, tuple(_yangsuite_menus.keys()))


def _register_menu_item(menu, text, url):
    """Add a new menu item linking to the given URL under the given menu.

    Args:
      menu (str): Name of an existing menu title.
      text (str): Text of the new menu item.
      url (str): Relative or absolute URL this menu item links to.
    """
    global _yangsuite_menus
    _yangsuite_menus[menu].append(YSMenuItem(text, url))
    log.debug("Added menu item '%s → %s' in menu '%s'",
              text, url, menu)
