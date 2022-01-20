#!/usr/bin/env python3
"""
Module COMMON -- Python UI Common Global Objects
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import sys
import os
import functools
import pkgutil

from plib.ui.defs import *
from plib.ui.toolkits import get_toolkit


# action dictionary
action_map = {
    ACTION_FILE_NEW: ["file_new", "&New", "Create new document"],
    ACTION_FILE_OPEN: ["file_open", "&Open", "Open document"],
    ACTION_FILE_SAVE: ["file_save", "&Save", "Save current document"],
    ACTION_FILE_SAVEAS: ["file_saveas", "Save &As", "Save current document with different filename"],
    ACTION_FILE_CLOSE: ["file_close", "&Close", "Close current document"],
    ACTION_VIEW: ["view", "&View", "View item"],
    ACTION_EDIT: ["edit", "&Edit", "Edit item"],
    ACTION_EDIT_UNDO: ["edit_undo", "&Undo", "Undo last operation"],
    ACTION_EDIT_REDO: ["edit_redo", "&Redo", "Redo last operation"],
    ACTION_EDIT_CUT: ["edit_cut", "Cu&t", "Cut selection to clipboard"],
    ACTION_EDIT_COPY: ["edit_copy", "&Copy", "Copy selection to clipboard"],
    ACTION_EDIT_PASTE: ["edit_paste", "&Paste", "Paste from clipboard"],
    ACTION_EDIT_DELETE: ["edit_delete", "&Delete", "Delete selection"],
    ACTION_EDIT_SELECTALL: ["edit_selectall", "Select &All", "Select all"],
    ACTION_EDIT_SELECTNONE: ["edit_selectnone", "Clear &Selection", "Clear selection"],
    ACTION_EDIT_OVERWRITE: ["edit_overwrite", "Toggle &Overwrite", "Toggle overwrite mode"],
    ACTION_EDIT_CLEAR: ["edit_clear", "Clear &Edit", "Clear document"],
    ACTION_REFRESH: ["refresh", "Re&fresh", "Refresh view"],
    ACTION_ADD: ["add", "A&dd", "Add item"],
    ACTION_REMOVE: ["remove", "Re&move", "Remove item"],
    ACTION_APPLY: ["apply", "&Apply", "Apply changes"],
    ACTION_COMMIT: ["commit", "Co&mmit", "Commit transaction"],
    ACTION_ROLLBACK: ["rollback", "Rollbac&k", "Roll back transaction"],
    ACTION_OK: ["ok", "&Ok", "Ok"],
    ACTION_CANCEL: ["cancel", "&Cancel", "Cancel"],
    ACTION_PREFS: ["prefs", "&Preferences...", "Edit preferences"],
    ACTION_ABOUT: ["about", "A&bout...", "About this program"],
    ACTION_ABOUT_TOOLKIT: [
        "about_toolkit",
        "Abou&t {}...".format(get_toolkit().strip('2').strip('5').capitalize()),
        "About this UI toolkit"
    ],
    ACTION_EXIT: ["exit", "E&xit", "Exit program"]
}

# action key list (needed to ensure proper ordering of actions,
# since the dictionary keys won't necessarily be ordered)

action_key_list = sorted(action_map.keys())


# Allow adding custom actions; must be called before any
# widgets are created

def add_action(key, name, caption, description, icon):
    if key in action_map:
        raise RuntimeError("Key {} is already in use".format(key))
    action_map[key] = [name, caption, description, icon]
    action_key_list.append(key)
    action_key_list.sort()


# Allow modifying existing actions

def modify_action(key, name=None, caption=None, description=None, icon=None):
    entry = action_map.get(key)
    if not entry:
        raise RuntimeError("Invalid action key: {}".format(key))
    items = (name, caption, description, icon)
    add_index = len(entry)
    for index, item in enumerate(items[:add_index]):
        if item:
            entry[index] = item
    add_items = items[add_index:]
    if add_items:
        entry[add_index:] = add_items


# utility functions to get fully qualified pixmap path name


def pxdata(name,
           pxfmt="images/{}.png".format, fmt="{}-{}".format,
           get_data=functools.partial(pkgutil.get_data, 'plib.ui')):
    
    for suffix in (get_toolkit(), sys.platform, os.name, None):
        try:
            data = get_data(pxfmt(fmt(name, suffix) if suffix else name))
        except OSError:
            data = None
        if data:
            return data
    if os.path.isfile(name):
        with open(name, 'rb') as f:
            data = f.read()
        return data


# Convenience functions for action properties

def action_name(action):
    return action_map[action][0]


def action_caption(action):
    return action_map[action][1]


def action_description(action):
    return action_map[action][2]


def action_icondata(action):
    props = action_map[action]
    # This hack allows the icon data key to be the name or be set separately
    return pxdata(props[3 if len(props) > 3 and props[3] else 0])


# Process font arguments to ensure all are filled in

def font_args(widget, font_name, font_size, bold, italic):
    if font_name is None:
        font_name = widget.get_font_name()
    if font_size is None:
        font_size = widget.get_font_size()
    if bold is None:
        bold = widget.get_font_bold()
    if italic is None:
        italic = widget.get_font_italic()
    return font_name, font_size, bold, italic
