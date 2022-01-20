#!/usr/bin/env python3
"""
Sub-Package UI.WIDGETS of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib.classtools import recurselist
from plib.stdlib.imp import import_from_module

from plib.ui.defs import *
from plib.ui.common import action_name
from plib.ui.toolkits import get_toolkit


# Toolkit-aware widget class retrieval function

def get_toolkit_class(modname, klassname):
    toolkit = get_toolkit()
    modname = "plib.ui.toolkits.{}.{}".format(toolkit, modname)
    return import_from_module(modname, klassname)


# Helper function to find and connect signals to handlers

WIDGET_EVENT_MAP = {
    SIGNAL_ACTIVATED: None,
    SIGNAL_CLICKED: 'clicked',
    SIGNAL_TOGGLED: 'toggled',
    SIGNAL_SELECTED: 'selected',
    SIGNAL_LISTVIEWSELECTED: 'selected',
    SIGNAL_LISTBOXSELECTED: 'selected',
    SIGNAL_CELLSELECTED: 'selected',
    SIGNAL_FOCUS_IN: 'focus_in',
    SIGNAL_FOCUS_OUT: 'focus_out',
    SIGNAL_CELLCHANGED: 'changed',
    SIGNAL_TEXTCHANGED: 'changed',
    SIGNAL_TEXTMODCHANGED: 'mod_changed',
    SIGNAL_TEXTSTATECHANGED: 'state_changed',
    SIGNAL_EDITCHANGED: 'changed',
    SIGNAL_ENTER: 'enter',
    SIGNAL_TABSELECTED: 'selected',
    SIGNAL_QUERYCLOSE: 'queryclose',
    SIGNAL_CLOSING: 'closing',
    SIGNAL_SHOWN: 'shown',
    SIGNAL_HIDDEN: 'hidden',
}


def setup_signal_handlers(manager, obj, name,
                          event_map=WIDGET_EVENT_MAP):
    
    for signal in recurselist(type(obj), 'signals'):
        event = event_map[signal]
        method = "on_{}_{}".format(name, event) if event else "on_{}".format(name)
        target = getattr(manager, method, None)
        if target:
            obj.setup_notify(signal, target)


# Basic widget construction function; this will end up getting called
# for each widget spec with the obvious arguments. The widget will
# automagically find its event handlers on the manager when it is constructed

WIDGET_ATTR_PREFIXES = {
    # Only widgets whose prefix is different from their module name need this
    'PCheckBox': 'checkbox',
    'PEditBox': 'edit',
    'PNumEditBox': 'edit',
    'PTreeView': 'treeview',
    'PEditControl': 'memo',
    'PTextDisplay': 'text',
    'PStatusLabel': 'label',
}


def widget_from_spec(manager, parent, modname, klassname, name, args, kwargs,
                     attr_prefixes=WIDGET_ATTR_PREFIXES):
    
    klass = get_toolkit_class(modname, klassname)
    attrname = "{}_{}".format(attr_prefixes.get(klassname, modname), name)
    widget = klass(manager, parent, *args, **kwargs)
    setattr(manager, attrname, widget)
    setup_signal_handlers(manager, widget, name)
    return widget


# Helper function for widgets that can have contents as list of specs

def widgets_from_contents(manager, parent, contents, callback=None):
    widgets = []
    for spec in contents:
        widget = widget_from_spec(manager, parent, *spec)
        if callback:
            callback(widget)
        widgets.append(widget)
    return widgets


# Widget spec convenience functions

def auto_name(prefix, num):
    prefix = '{}_'.format(prefix)
    num[0] += 1
    return '{}{}'.format(prefix, num[0])


## Widget spec functions ##


# Buttons have a caption and optional icon
# Buttons fire SIGNAL_CLICKED

def button(name, caption, icon=None):
    args = (caption,)
    kwargs = dict(
        icon=icon,
        geometry=(None, None, BUTTON_WIDTH, None),
    )
    return ('button', 'PButton', name, args, kwargs)


# Action buttons take their caption and icon from a menu/toolbar action
# Action buttons fire SIGNAL_ACTIVATED when clicked

def action_button(action):
    name = action_name(action)
    args = (action,)
    kwargs = dict(
        geometry=(None, None, BUTTON_WIDTH, None),
    )
    return ('button', 'PActionButton', name, args, kwargs)


# Check boxes have a label and checked state
# Check boxes fire SIGNAL_TOGGLED

def checkbox(name, label, checked=None):
    args = (label, checked)
    return ('button', 'PCheckBox', name, args, {})


def base_combo(klassname, name, items, value, **kwds):
    args = (items,)
    kwargs = dict(
        value=value,
    )
    kwargs.update(kwds)
    return ('combo', klassname, name, args, kwargs)


# Combo boxes have a string value and a drop-down list of choices
# Combo boxes fire SIGNAL_SELECTED

def combo(name, items=None, value=None, geometry=None):
    return base_combo('PComboBox', name, items, value, geometry=geometry)


# Numeric combo boxes present their values as ints instead of string

def num_combo(name, items=None, value=None, geometry=None):
    return base_combo('PNumComboBox', name, items, value, geometry=geometry)


# Sorted combo boxes sort their strings in the drop-down list

def sorted_combo(name, items, value=None, key=None, geometry=None):
    return base_combo('PSortedComboBox', name, items, value, geometry=geometry, key=key)


def base_edit(klassname, name, value, geometry, expand=True):
    args = (value,)
    kwargs = dict(
        geometry=geometry,
        expand=expand,
    )
    return ('editctrl', klassname, name, args, kwargs)


# Edit boxes are single-line string editors and can be initialized with a value;
# they default to automatically expanding horizontally to fill available space
# Edit boxes fire: SIGNAL_EDITCHANGED when their content is changed
#                  SIGNAL_ENTER when Enter is pressed (normally used to trigger an action)

def edit(name, text="", geometry=None, expand=True):
    #geometry = geometry or (None, None, EDIT_WIDTH, None)
    return base_edit('PEditBox', name, text, geometry, expand=expand)


# Numeric edit boxes present their value as an int instead of a string

def num_edit(name, value=0, geometry=None, expand=True):
    #geometry = geometry or (None, None, NUM_EDIT_WIDTH, None)
    return base_edit('PNumEditBox', name, value, geometry, expand=expand)


# Group boxes organize child controls; they automatically expand to
# fill available space; contents must be an iterable of widget specs

def groupbox(caption, contents,
             num=[0]):
    
    name = auto_name('groupbox', num)
    args = (caption,)
    kwargs = dict(
        contents=contents,
        margin=TAB_MARGIN,
        spacing=PANEL_SPACING,
    )
    return ('groupbox', 'PGroupBox', name, args, kwargs)


# A label displays its caption string

def label(name, caption, geometry=None, font=None):
    #geometry = geometry or (None, None, LABEL_WIDTH, None)
    args = (caption,)
    kwargs = dict(
        geometry=geometry,
        font=font,
    )
    return ('label', 'PTextLabel', name, args, kwargs)


def base_listbox(klassname, name, items, value, **kwargs):
    args = (items, value)
    return ('listbox', klassname, name, args, kwargs)


# List boxes display a list of strings
# List boxes fire SIGNAL_LISTBOXSELECTED

def listbox(name, items=None, value=None, geometry=None):
    #geometry = geometry or (None, None, LIST_WIDTH, LIST_HEIGHT)
    return base_listbox('PListBox', name, items, value, geometry=geometry)


# Sorted list boxes sort their displayed list of strings

def sorted_listbox(name, items=None, value=None, key=None, geometry=None):
    #geometry = geometry or (None, None, LIST_WIDTH, LIST_HEIGHT)
    return base_listbox('PSortedListBox', name, items, value, key=key, geometry=geometry)


def base_listview(klassname, name, labels, **kwds):
    kwargs = dict(
        labels=labels,
    )
    kwargs.update(kwds)
    return ('listview', klassname, name, (), kwargs)


# List views display rows each with one or more columns of strings, plus a header;
# they automatically expand to fill available space
# List views appear in code as sequences of tuples of strings
# List views fire SIGNAL_LISTVIEWSELECTED

def listview(name, labels=None, data=None, font=None, header_font=None):
    return base_listview('PListView', name, labels=labels, data=data,
                         font=font, header_font=header_font)


# Sorted list views sort their displayed rows, treating each row as a tuple of strings

def sorted_listview(name, labels=None, data=None, key=None, font=None, header_font=None):
    return base_listview('PSortedListView', name, labels=labels, data=data, key=key,
                         font=font, header_font=header_font)


# Tree views display a tree of items, each with one or more columns of strings, plus a header;
# they automatically expand to fill available space
# Tree views appear in code as sequences of 2-tuples (cols, children), where cols is a tuple
# of strings and children is another sequence of 2-tuples (cols, children)
# Tree views fire SIGNAL_LISTVIEWSELECTED

def treeview(name, labels=None, data=None, auto_expand=False, font=None, header_font=None):
    return base_listview('PTreeView', name, labels=labels, data=data, auto_expand=auto_expand,
                         font=font, header_font=header_font)


# Edit controls (memos) are multi-line scrolling plain text editors;
# they automatically expand to fill available space
# Edit controls fire: SIGNAL_TEXTCHANGED when their text is changed
#                     SIGNAL_TEXTSTATECHANGED when their text selection state is changed

def memo(name, scrolling=True, font=None):
    kwargs = dict(
        scrolling=scrolling,
        font=font,
    )
    return ('editctrl', 'PEditControl', name, (), kwargs)


# Padding is a blank panel that automatically expands to fill available space;
# it can be used to help align other widgets in layouts

def padding(num=[0]):
    name = auto_name('padding', num)
    return ('form', 'PPanel', name, (), {})


# The contents for all panels must be an iterable of widget specs

def base_panel(align, layout, contents, style=PANEL_NONE, margin=-1, spacing=-1,
               num=[0]):
    
    name = auto_name('panel', num)
    args = (align, layout)
    kwargs = dict(
        contents=contents,
        style=style,
        margin=margin,
        spacing=spacing,
    )
    return ('form', 'PPanel', name, args, kwargs)


# Frames are top-level layouts typically used as the main widget in an application to
# organize the layout of multiple sub-widgets; they automatically expand to fill
# available space

def frame(align, layout, contents, style=PANEL_NONE):
    return base_panel(align, layout, contents, style=style, margin=FRAME_MARGIN, spacing=PANEL_SPACING)


# Panels are layout widgets typically used as sub-widgets to frames in complex
# layouts; they automatically expand to fill available space

def panel(align, layout, contents, style=PANEL_NONE):
    return base_panel(align, layout, contents, style=style, margin=PANEL_MARGIN, spacing=PANEL_SPACING)


# Tabs are panels specialized to organize multiple widgets in a tab widget's tab;
# they automatically expand to fill available space

def tab(align, layout, contents, style=PANEL_NONE):
    return base_panel(align, layout, contents, style=style, margin=TAB_MARGIN, spacing=PANEL_SPACING)


# Boxes are simple containers typically used at the bottom level of layouts;
# they automatically expand to fill available space

def box(align, layout, contents, style=PANEL_NONE):
    return base_panel(align, layout, contents, style=style, margin=BOX_MARGIN, spacing=PANEL_SPACING)


# Tables are grid-style widgets with multiple rows and columns plus a header;
# they automatically expand to fill available space

def table(name, labels=None, data=None, font=None, header_font=None):
    kwargs = dict(
        labels=labels,
        data=data,
        font=font,
        header_font=header_font,
    )
    return ('table', 'PTable', name, (), kwargs)


# Tab widgets organize complex layouts in multiple tabs; they automatically expand
# to fill available space; tabs must be an iterable of widget specs

def tabwidget(name, tabs):
    kwargs = dict(
        tabs=tabs,
    )
    return ('tabwidget', 'PTabWidget', name, (), kwargs)


# Text displays are scrolling widgets that show multiple lines of plain text;
# they automatically expand to fill available space

def text(name, text="", scrolling=True, font=None):
    args = (text,)
    kwargs = dict(
        scrolling=scrolling,
        font=font,
    )
    return ('display', 'PTextDisplay', name, args, kwargs)


# Containers are wrappers around widgets that are not directly supported
# by PLIB.UI; the add_child method is used to add the custom widget as
# a single child widget of the container

def container(name):
    return ('container', 'PContainer', name, (), {})


# Convenience function for labeled controls

def labeled(caption, control, layout=LAYOUT_VERTICAL, align=ALIGN_JUST, label_bold=True):
    name = '{}_label'.format(control[2])  # control will be a widget spec tuple
    label_align = (ALIGN_TOP if layout == LAYOUT_VERTICAL else ALIGN_LEFT)
    return box(align, layout, [
        box(label_align, LAYOUT_HORIZONTAL, [
            label(name, caption, font=(None, None, label_bold)),
        ]),
        control
    ])

# Label boxes work like group boxes but allow a bold label without making
# every widget in the box bold also

def labelbox(caption, contents, layout=LAYOUT_VERTICAL, align=ALIGN_JUST, style=PANEL_NONE, label_bold=True,
             num=[0]):
    
    name = auto_name('labelbox', num)
    contents = panel(ALIGN_JUST, layout, contents, style=style)
    return box(align, LAYOUT_VERTICAL, [
        label(name, caption, font=(None, None, label_bold)),
        contents
    ])
