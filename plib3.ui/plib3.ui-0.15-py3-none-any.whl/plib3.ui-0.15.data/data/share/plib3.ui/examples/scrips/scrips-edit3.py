#!/usr/bin/env python3
"""
SCRIPS-EDIT.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Editor for scrips.dat file used to keep track of
prescription refills.
"""

import sys
import os
import datetime
import email.charset

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui import common
from plib.ui.app import PApplication
from plib.ui.prefs import PPreferences
from plib.ui.widgets import *


def _load_example_module():
    from plib.stdlib.imp import import_from_path
    from plib.stdlib.postinstall import get_share_dir
    
    return import_from_path(
        os.path.join(
            get_share_dir('plib3.stdlib', 'plib.stdlib'),
            'examples', 'scrips'
        ),
        'scrips3'
    )


scrips = _load_example_module()


# Add custom actions
ACTION_SUBMIT = ACTION_OK + 1
ACTION_REFILL = ACTION_REFRESH + 1

common.add_action(
    ACTION_SUBMIT,
    'submit', "&Submit", "Submit prescription for refill", "ok"
)

common.add_action(
    ACTION_REFILL,
    'refill', "&Refill", "Complete prescription refill", "refresh"
)

# Modify some action descriptions
common.modify_action(ACTION_FILE_SAVE, description="Save prescription list")
common.modify_action(ACTION_ADD, description="Add prescription to list")
common.modify_action(ACTION_REMOVE, description="Remove prescription from list")


# Last item in each tuple is character column width for text output

SCRIP_HEADINGS = [
    ("Drug", 150, 16),
    ("Rx", 100, 12),
    ("Last Filled", 100, ALIGN_CENTER, 16),
    ("Days", 100, ALIGN_CENTER, 8),
    ("Refills Left", 100, ALIGN_CENTER, 16),
    ("Submitted", 100, 0)
]


def output_label(index, heading):
    return "{}{}".format(("#" if index == 0 else ""), heading[0]).ljust(heading[-1])


class ScripEditable(scrips.Scrip):
    
    init_name = "<Name>"
    init_rxnum = "<Rx#>"
    init_days = 30
    init_refills = 0
    init_submitted = False
    
    headings = SCRIP_HEADINGS
    
    def __init__(self, *tokens):
        if not tokens:
            # The default of today's date takes care of the filldate field
            # since there's no init class field for it
            tokens = [
                str(getattr(self, 'init_{}'.format(name), datetime.date.today()))
                for name in self._fields
            ]
        scrips.Scrip.__init__(self, *tokens)
    
    def submit(self):
        if self.refills < 1:
            return False
        # TODO: actually send the email here?
        self.submitted = True
        return True
    
    def refill(self):
        if not self.submitted:
            return False
        self.filldate = datetime.date.today()
        self.refills -= 1
        self.submitted = False
        return True
    
    def output_line(self):
        return "".join([
            str(self[col]).ljust(heading[-1])
            for col, heading in enumerate(self.headings)
        ])


class ScripListEditor(PApplication):
    
    about_data = {
        'name': "ScripsEdit",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "Prescription Editor",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net",
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    prefs_data = (scrips.inifile, SECTION_GROUPBOX, {
        "email": "E-Mail Fields",
        "email_fromaddr": "From",
        "email_toaddr": "To",
        "email_typestr": "MIME Type",
        "email_charsetstr": "Character Set",
        "email_serverstr": "Server Hostname",
        "email_portnum": "Server Port",
        "email_username": "User Name",
        "email_password": "Password",
        "headers": "E-Mail Headers",
        "headers_dict": "Python Dictionary",
        "pharmacy": "Pharmacy",
        "pharmacy_name": "Name",
    })
    
    prefs_dialog_enums = {
        "email_typestr": (
            "text/plain",
            "text/html",
        ),
        "email_charsetstr": tuple(sorted(
            email.charset.CHARSETS.keys()
        )),
        "email_portnum": (
            (25, "Plain SMTP"),
            (465, "Old SMTP/TLS"),
            (587, "SMTP/TLS"),
        ),
    }
    
    prefs_dialog_groups = {
        "email": (
            ("email_fromaddr", "email_toaddr"),
            ("email_typestr", "email_charsetstr"),
            ("email_serverstr", "email_portnum"),
            ("email_username", "email_password"),
        ),
    }
    
    prefs_dialog_width = 640
    
    menu_actions = [
        (MENU_FILE, (ACTION_FILE_SAVE, ACTION_EXIT,)),
        (MENU_ACTION, (ACTION_SUBMIT, ACTION_REFILL, ACTION_ADD, ACTION_REMOVE,)),
        (MENU_OPTIONS, (ACTION_PREFS,)),
        (MENU_HELP, (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,)),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_SAVE,),
        (ACTION_SUBMIT, ACTION_REFILL, ACTION_ADD, ACTION_REMOVE,),
        (ACTION_PREFS, ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    main_title = "Prescription List Editor"
    main_iconfile = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                 "scrips.png")
    
    main_size = SIZE_CLIENTWRAP
    main_placement = MOVE_CENTER
    
    headings = SCRIP_HEADINGS
    
    table_font_size = 16 if sys.platform == 'darwin' else 12
    
    main_widget = table('scrips', [heading[:-1] for heading in headings],
                        font=("Arial", table_font_size),
                        header_font=("Arial", table_font_size, True))
    
    large_icons = True
    show_labels = True
    
    filename = scrips.scrips_dat_file()
    
    def after_create(self):
        self.prefs = PPreferences(self, "ScripsEdit Preferences")
        self.data = scrips.scriplist(ScripEditable)
        self.table_scrips.extend(self.data)
        for row in range(len(self.data)):
            self.set_colors(row)
        self.main_window.statusbar.set_text("Editing prescription info.")
        self.pending = False
        self.modified = False
        self.update_pending()
        self.update_size()
    
    def update_pending(self):
        self.pending = any(
            (self.data[row].due() and not self.data[row].submitted)
            for row in range(len(self.data))
        )
    
    def set_colors(self, row=None):
        if row is None:
            row = self.table_scrips.current_row()
        scrip = self.data[row]
        if scrip.due():
            if scrip.submitted:
                self.table_scrips.set_row_fgcolor(row, COLOR_BLACK)
            else:
                self.table_scrips.set_row_fgcolor(row, COLOR_RED)
            self.table_scrips.set_row_bkcolor(row, COLOR_YELLOW)
        else:
            self.table_scrips.set_row_fgcolor(row, COLOR_BLACK)
            self.table_scrips.set_row_bkcolor(row, COLOR_WHITE)
    
    def update_row(self, row):
        self.set_colors(row)
        self.update_pending()
    
    def on_scrips_changed(self, row, col):
        self.data[row][col] = self.table_scrips[row][col]
        self.update_row(row)
        self.modified = True
    
    def header_line(self):
        return "{}".format("".join([
            output_label(index, heading) for index, heading in enumerate(self.headings)
        ]))
    
    def output_lines(self):
        return os.linesep.join(
            [self.header_line()] +
            [scrip.output_line() for scrip in self.data]
        )
    
    def save_scrips(self):
        lines = self.output_lines()
        with open(self.filename, 'w') as f:
            f.writelines(lines)
        self.modified = False
    
    def on_file_save(self):
        self.save_scrips()
    
    def update_state(self, row):
        self.table_scrips[row][:] = self.data[row]
        self.update_row(row)
        self.modified = True
    
    def on_submit(self):
        row = self.table_scrips.current_row()
        if self.data[row].submit():
            self.update_state(row)
        else:
            self.message_box.error("Submit Error", "No refills left.")
    
    def on_refill(self):
        row = self.table_scrips.current_row()
        if self.data[row].refill():
            self.update_state(row)
        else:
            self.message_box.error("Refill Error", "Refill must be submitted first.")
    
    def update_size(self):
        width, height = self.table_scrips.minwidth(), self.table_scrips.minheight()
        self.table_scrips.set_min_size(width, height)
        self.main_window.set_client_area_size(width, height)
    
    def on_add(self):
        scrip = ScripEditable()
        self.data.append(scrip)
        self.table_scrips.append(scrip)
        self.update_pending()
        self.update_size()
        self.modified = True
    
    def on_remove(self):
        scripname = self.data[self.current_row()].name
        msg = "Do you really want to delete {}?".format(scripname)
        if self.message_box.query2("Delete Prescription", msg) == ANSWER_OK:
            row = self.table_scrips.current_row()
            del self.table_scrips[row]
            del self.data[row]
            self.update_pending()
            self.update_size()
            self.modified = True
    
    def on_prefs(self):
        self.prefs.show_dialog()
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()
    
    def accept_close(self):
        if self.pending:
            abort_answer = self.message_box.query2(
                "Pending Submissions",
                "Pending scrips not submitted. Exit anyway?"
            )
            if abort_answer == ANSWER_CANCEL:
                return False
        if self.modified:
            save_answer = self.message_box.query2(
                "Unsaved Changes",
                "Scrips changes not saved. Exit without saving?"
            )
            return (save_answer == ANSWER_OK)
        return True


if __name__ == "__main__":
    ScripListEditor().run()
