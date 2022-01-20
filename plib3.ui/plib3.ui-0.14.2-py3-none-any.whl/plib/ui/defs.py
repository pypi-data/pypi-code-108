#!/usr/bin/env python3
"""
Module DEFS -- Common UI Definitions
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines common constants and functions used by various UI modules.
"""

import sys

# general constants
DEFAULT_FONT_SIZE = 10

# constants for referring to UI toolkits
#UI_QT = 1
#UI_GTK = 2
UI_WX = 3
#UI_KDE = 4
UI_QT4 = 5
UI_KDE4 = 6
UI_PYSIDE = 7
UI_QT5 = 8
UI_PYSIDE2 = 9
UI_WEB = 10

# message box types
MBOX_INFO = 0
MBOX_WARN = 1
MBOX_ERROR = 2
MBOX_QUERY = 3

# constants for message box responses
ANSWER_NONE = 0
ANSWER_YES = 1
ANSWER_NO = 2
ANSWER_CANCEL = 3
ANSWER_OK = 4

# constants for alignment
ALIGN_LEFT = 1
ALIGN_CENTER = 2
ALIGN_RIGHT = 3
ALIGN_TOP = 4
ALIGN_BOTTOM = 5
ALIGN_JUST = 9

# Layout constants
LAYOUT_NONE = 0
LAYOUT_HORIZONTAL = 1
LAYOUT_VERTICAL = 2

# Panel style constants
PANEL_NONE = 0
PANEL_BOX = 1
PANEL_RAISED = 2
PANEL_SUNKEN = 3

# Prefs dialog section style constants
SECTION_TAB = 0  # this is the default
SECTION_GROUPBOX = 1

# constants for signals
SIGNAL_ACTIVATED = 10  # widget has received focus
SIGNAL_CLICKED = 101  # widget has been clicked
SIGNAL_TOGGLED = 102  # on/off widget has been toggled
SIGNAL_SELECTED = 151  # item in widget has been selected; handler must take index param
SIGNAL_LISTVIEWSELECTED = 161  # list view item has changed; handler must take item param
SIGNAL_LISTBOXSELECTED = 165  # list box item has changed; handler must take item param
SIGNAL_CELLSELECTED = 171  # table current cell has changed; handler must take row, col params
SIGNAL_FOCUS_IN = 191  # widget has received keyboard focus
SIGNAL_FOCUS_OUT = 195  # widget has lost keyboard focus
SIGNAL_CELLCHANGED = 301  # table cell text has changed; handler must take row, col params for changed cell
SIGNAL_TEXTCHANGED = 401  # text in edit control has been changed
SIGNAL_TEXTMODCHANGED = 406  # modification state of edit control has changed
SIGNAL_TEXTSTATECHANGED = 411  # state of edit control has changed
SIGNAL_EDITCHANGED = 450  # text in edit box has been changed
SIGNAL_ENTER = 490  # enter/return key has been pressed while widget has focus
SIGNAL_TABSELECTED = 501  # new tab has been selected; handler must take int param for new index
SIGNAL_FINISHED = 601  # dialog is finished
SIGNAL_QUERYCLOSE = 921  # widget is asking permission to close
SIGNAL_CLOSING = 931  # widget close has been accepted
SIGNAL_SHOWN = 941  # widget has been shown
SIGNAL_HIDDEN = 951  # widget has been hidden

# these signal constants are for internal use only
SIGNAL_MENUACTIVATED = 19  # internal menu/toolbar activation signal that gets re-interpreted
SIGNAL_KEYPRESSED = 499  # internal key pressed signal, filtered to SIGNAL_ENTER
SIGNAL_TABCURRENTCHANGED = 599  # internal tab changed signal that gets re-interpreted
SIGNAL_NOTIFIER = 801  # socket notifier has received an event notification
SIGNAL_TABLECELLSELECTED = 829  # internal table cell selected signal that gets re-interpreted
SIGNAL_TABLECHANGED = 831  # internal table changed event that gets re-interpreted
SIGNAL_TABLECELLEDITING = 835  # internal table cell edit event to track changes
SIGNAL_TABLECELLEDITDONE = 839  # internal table cell edit event to track changes
SIGNAL_WIDGETCHANGED = 901  # widget has been changed (not including above specific changes)
SIGNAL_SIZEEVENT = 935  # internal window size event that gets re-interpreted
SIGNAL_SHOWEVENT = 945  # internal window show/hide event that gets re-interpreted
SIGNAL_MINIMIZEEVENT = 955  # internal window minimize event that gets re-interpreted
SIGNAL_CLOSEEVENT = 989  # internal main window close event that gets re-interpreted
SIGNAL_BEFOREQUIT = 999  # app is about to quit

# constants for action flags, used as keys
ACTION_FILE_NEW = 5
ACTION_FILE_OPEN = 10
ACTION_FILE_SAVE = 15
ACTION_FILE_SAVEAS = 20
ACTION_FILE_CLOSE = 25
ACTION_EDIT_UNDO = 260
ACTION_EDIT_REDO = 270
ACTION_EDIT_CUT = 310
ACTION_EDIT_COPY = 320
ACTION_EDIT_PASTE = 330
ACTION_EDIT_DELETE = 340
ACTION_EDIT_SELECTALL = 350
ACTION_EDIT_SELECTNONE = 355
ACTION_EDIT_CLEAR = 360
ACTION_EDIT_OVERWRITE = 390
ACTION_VIEW = 500
ACTION_EDIT = 505
ACTION_OK = 550
ACTION_CANCEL = 660
ACTION_REFRESH = 880
ACTION_ADD = 1024
ACTION_REMOVE = 2048
ACTION_APPLY = 8192
ACTION_COMMIT = 8288
ACTION_ROLLBACK = 8298
ACTION_PREFS = 9000
ACTION_ABOUT = 9152
ACTION_ABOUT_TOOLKIT = 9160
ACTION_EXIT = 9999

# Menu titles

MENU_FILE = "&File"
MENU_EDIT = "&Edit"
MENU_ACTION = "&Action"
MENU_OPTIONS = "&Options"
MENU_HELP = "&Help"

# color constants -- we choose values to make hacks easier :)
COLORNAMES = [
    'BLACK',
    'DARKRED', 'RED',  # 'LIGHTRED', # FIXME: for some reason this isn't in the standard X11 list
    'DARKGREEN', 'GREEN', 'LIGHTGREEN',
    'DARKBLUE', 'BLUE', 'LIGHTBLUE',
    'YELLOW', 'MAGENTA', 'CYAN',
    'DARKGRAY', 'GRAY', 'LIGHTGRAY', 'WHITE'
]
for color in COLORNAMES:
    setattr(sys.modules[__name__], 'COLOR_{}'.format(color), color)

# top window geometry constants
SIZE_NONE = 0
SIZE_CLIENTWRAP = 1
SIZE_MAXIMIZED = 2
SIZE_OFFSET = 4
SIZE_SETTINGS = 8
SIZE_DESKTOP = 16

MOVE_NONE = 0
MOVE_CENTER = 1
MOVE_SETTINGS = 2

# Socket notifier constants
NOTIFY_READ = 0
NOTIFY_WRITE = 1

# Control variables for widget geometries

FRAME_MARGIN = 10
TAB_MARGIN = 10
PANEL_MARGIN = 4
BOX_MARGIN = 1
PANEL_SPACING = 10
BUTTON_WIDTH = 110

# Width values for headers; a number > 0 means set to that width

WIDTH_CONTENTS = 0
WIDTH_STRETCH = -1

# Convenience function to add or mutate constants; must
# be called before any other module besides this one is
# imported

def add_constants(**kw):
    for name, value in kw.items():
        setattr(sys.modules[__name__], name, value)
