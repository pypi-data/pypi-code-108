#!/usr/bin/env python3
"""
UI-DISPLAY.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A demo app that displays all of the available UI actions
and their associated images, and demonstrates how event
handlers are defined.
"""

import sys

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.widgets import *


class UIDisplayTester(PApplication):
    
    about_data = {
        'name': "UIDisplayTester",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "UI Display Demo",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net"
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    menu_actions = [
        (MENU_FILE, (
            ACTION_FILE_NEW, ACTION_FILE_OPEN, ACTION_FILE_SAVE, ACTION_FILE_SAVEAS,
            ACTION_FILE_CLOSE, ACTION_EXIT,
        )),
        (MENU_EDIT, (
            ACTION_EDIT_UNDO, ACTION_EDIT_REDO,
            ACTION_EDIT_CUT, ACTION_EDIT_COPY, ACTION_EDIT_PASTE,
            ACTION_EDIT_DELETE, ACTION_EDIT_SELECTALL, ACTION_EDIT_SELECTNONE, ACTION_EDIT_CLEAR,
        )),
        (MENU_ACTION, (
            ACTION_VIEW, ACTION_EDIT, ACTION_APPLY, ACTION_REFRESH,
            ACTION_OK, ACTION_CANCEL,
            ACTION_ADD, ACTION_REMOVE,
            ACTION_COMMIT, ACTION_ROLLBACK,
        )),
        (MENU_OPTIONS, (
            ACTION_PREFS,
        )),
        (MENU_HELP, (
            ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,
        )),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_NEW, ACTION_FILE_OPEN, ACTION_FILE_SAVE, ACTION_FILE_SAVEAS, ACTION_FILE_CLOSE,),
        (ACTION_EDIT_UNDO, ACTION_EDIT_REDO,),
        (ACTION_EDIT_CUT, ACTION_EDIT_COPY, ACTION_EDIT_PASTE,),
        (ACTION_EDIT_DELETE, ACTION_EDIT_SELECTALL, ACTION_EDIT_SELECTNONE, ACTION_EDIT_CLEAR,),
        (ACTION_VIEW, ACTION_EDIT, ACTION_APPLY, ACTION_REFRESH,),
        (ACTION_OK, ACTION_CANCEL,),
        (ACTION_ADD, ACTION_REMOVE,),
        (ACTION_COMMIT, ACTION_ROLLBACK,),
        (ACTION_PREFS, ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    status_labels = [
        ('action', "", PANEL_SUNKEN),
    ]
    
    main_title = "UI Display Demo"
    
    main_size = SIZE_MAXIMIZED
    
    main_widget = text('output', "PLIB3 UI Display Demo Application.",
                       font=("Courier New", 12))
    
    query_on_exit = False
    
    def set_status_text(self, text):
        print(text)
        self.main_window.statusbar.set_text(text)
        self.label_action.caption = text
    
    def on_file_new(self):
        self.set_status_text("ACTION_FILE_NEW")
    
    def on_file_open(self):
        self.set_status_text("ACTION_FILE_OPEN")
    
    def on_file_save(self):
        self.set_status_text("ACTION_FILE_SAVE")
    
    def on_file_saveas(self):
        self.set_status_text("ACTION_FILE_SAVEAS")
    
    def on_file_close(self):
        self.set_status_text("ACTION_FILE_CLOSE")
    
    def on_edit_undo(self):
        self.set_status_text("ACTION_EDIT_UNDO")
    
    def on_edit_redo(self):
        self.set_status_text("ACTION_EDIT_REDO")
    
    def on_edit_cut(self):
        self.set_status_text("ACTION_EDIT_CUT")
    
    def on_edit_copy(self):
        self.set_status_text("ACTION_EDIT_COPY")
    
    def on_edit_paste(self):
        self.set_status_text("ACTION_EDIT_PASTE")
    
    def on_edit_delete(self):
        self.set_status_text("ACTION_EDIT_DELETE")
    
    def on_edit_selectall(self):
        self.set_status_text("ACTION_EDIT_SELECTALL")
    
    def on_edit_selectnone(self):
        self.set_status_text("ACTION_EDIT_SELECTNONE")
    
    def on_edit_clear(self):
        self.set_status_text("ACTION_EDIT_CLEAR")
    
    def on_view(self):
        self.set_status_text("ACTION_VIEW")
    
    def on_edit(self):
        self.set_status_text("ACTION_EDIT")
    
    def on_refresh(self):
        self.set_status_text("ACTION_REFRESH")
    
    def on_add(self):
        self.set_status_text("ACTION_ADD")
    
    def on_remove(self):
        self.set_status_text("ACTION_REMOVE")
    
    def on_apply(self):
        self.set_status_text("ACTION_APPLY")
    
    def on_commit(self):
        self.set_status_text("ACTION_COMMIT")
    
    def on_rollback(self):
        self.set_status_text("ACTION_ROLLBACK")
    
    def on_ok(self):
        self.set_status_text("ACTION_OK")
    
    def on_cancel(self):
        self.set_status_text("ACTION_CANCEL")
    
    def on_prefs(self):
        self.set_status_text("ACTION_PREFS")
    
    def on_about(self):
        self.set_status_text("ACTION_ABOUT")
        self.about()
    
    def on_about_toolkit(self):
        self.set_status_text("ACTION_ABOUT_TOOLKIT")
        self.about_toolkit()
    
    def on_exit(self):
        self.set_status_text("ACTION_EXIT")
        self.exit_app()
    
    def accept_close(self):
        return (not self.query_on_exit) or self.message_box.query2(
            "Application Exit",
            "Exit {}?".format(self.about_data['name'])
        ) == ANSWER_OK


if __name__ == "__main__":
    from plib.stdlib.options import parse_options
    optlist = (
        ("-l", "--large-icons", {
            'action': "store_true",
            'dest': "large_icons", 'default': False,
            'help': "Use large toolbar icons"
        }),
        ("-s", "--show-labels", {
            'action': "store_true",
            'dest': "show_labels", 'default': False,
            'help': "Show toolbar button labels"
        }),
        ("-q", "--query-on-exit", {
            'action': "store_true",
            'dest': "query_on_exit", 'default': False,
            'help': "Ask for confirmation on app exit"
        }),
    )
    opts, args = parse_options(optlist)
    # The options object supports a dictionary interface,
    # making it easy to update class fields from it
    for opt, value in opts.items():
        setattr(UIDisplayTester, opt, value)
    UIDisplayTester().run()
