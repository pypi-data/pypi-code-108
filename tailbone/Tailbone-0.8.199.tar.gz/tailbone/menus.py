# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
App Menus
"""

from __future__ import unicode_literals, absolute_import

from rattail.core import Object
from rattail.util import import_module_path


class MenuGroup(Object):
    title = None
    items = None
    is_menu = True
    is_link = False


class MenuItem(Object):
    title = None
    url = None
    target = None
    is_link = True
    is_menu = False
    is_sep = False


class MenuItemMenu(Object):
    title = None
    items = None
    is_menu = True
    is_sep = False


class MenuSeparator(object):
    is_menu = False
    is_sep = True


def make_simple_menus(request):
    """
    Build the main menu list for the app.
    """
    menus_module = import_module_path(
        request.rattail_config.require('tailbone', 'menus'))

    if not hasattr(menus_module, 'simple_menus') or not callable(menus_module.simple_menus):
        raise RuntimeError("module does not have a simple_menus() callable: {}".format(menus_module))

    # collect "simple" menus definition, but must refine that somewhat to
    # produce our final menus
    raw_menus = menus_module.simple_menus(request)
    mark_allowed(request, raw_menus)
    final_menus = []
    for topitem in raw_menus:

        if topitem['allowed']:

            if topitem.get('type') == 'link':
                final_menus.append(make_menu_entry(topitem))

            else: # assuming 'menu' type

                menu_items = []
                for item in topitem['items']:
                    if not item['allowed']:
                        continue

                    # nested submenu
                    if item.get('type') == 'menu':
                        submenu_items = []
                        for subitem in item['items']:
                            if subitem['allowed']:
                                submenu_items.append(make_menu_entry(subitem))
                        menu_items.append(MenuItemMenu(
                            title=item['title'],
                            items=submenu_items))

                    elif item.get('type') == 'sep':
                        # we only want to add a sep, *if* we already have some
                        # menu items (i.e. there is something to separate)
                        # *and* the last menu item is not a sep (avoid doubles)
                        if menu_items and not menu_items[-1].is_sep:
                            menu_items.append(make_menu_entry(item))

                    else: # standard menu item
                        menu_items.append(make_menu_entry(item))

                # remove final separator if present
                if menu_items and menu_items[-1].is_sep:
                    menu_items.pop()

                # only add if we wound up with something
                assert menu_items
                if menu_items:
                    final_menus.append(MenuGroup(
                        title=topitem['title'],
                        items=menu_items))

    return final_menus


def make_menu_entry(item):
    """
    Convert a simple menu entry dict, into a proper menu-related object, for
    use in constructing final menu.
    """
    # separator
    if item.get('type') == 'sep':
        return MenuSeparator()

    # standard menu item
    return MenuItem(
        title=item['title'],
        url=item['url'],
        target=item.get('target'))


def is_allowed(request, item):
    """
    Logic to determine if a given menu item is "allowed" for current user.
    """
    perm = item.get('perm')
    if perm:
        return request.has_perm(perm)
    return True


def mark_allowed(request, menus):
    """
    Traverse the menu set, and mark each item as "allowed" (or not) based on
    current user permissions.
    """
    for topitem in menus:

        if topitem.get('type', 'menu') == 'menu':
            topitem['allowed'] = False

            for item in topitem['items']:

                if item.get('type') == 'menu':
                    for subitem in item['items']:
                        subitem['allowed'] = is_allowed(request, subitem)

                    item['allowed'] = False
                    for subitem in item['items']:
                        if subitem['allowed'] and subitem.get('type') != 'sep':
                            item['allowed'] = True
                            break

                else:
                    item['allowed'] = is_allowed(request, item)

            for item in topitem['items']:
                if item['allowed'] and item.get('type') != 'sep':
                    topitem['allowed'] = True
                    break
