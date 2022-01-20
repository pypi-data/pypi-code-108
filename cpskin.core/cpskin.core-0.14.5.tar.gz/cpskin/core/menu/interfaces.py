# -*- coding: utf-8 -*-
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem


class IConfigurationsSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the cpskin configurations menu.
    """


class IConfigurationsMenu(IBrowserMenu):
    """The configurations menu.

    This gets its menu items from portal_actions.
    """
