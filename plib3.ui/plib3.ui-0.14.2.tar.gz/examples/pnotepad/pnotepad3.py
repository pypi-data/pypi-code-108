#!/usr/bin/env python3
"""
PNOTEPAD.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple plain text editor.
"""

import sys
import os

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.textfile import PTextFile
from plib.ui.widgets import *


class PMemoFile(PTextFile):
    
    untitled = object()
    
    def __init__(self, app, control):
        PTextFile.__init__(self, app, control, [
            ("Text Files", ["txt"]),
            ("All Files", ["*"]),
        ])
        self.main_window = app.main_window
        self.base_title = app.main_title
    
    def set_filename(self, filename):
        super(PMemoFile, self).set_filename(filename)
        if filename:
            self.main_window.set_caption("{} - {}".format(
                self.base_title,
                "<Untitled>" if filename is self.untitled else filename
            ))
        else:
            self.main_window.set_caption(self.base_title)


class PNotepad(PApplication):
    
    about_data = {
        'name': "PNotepad",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "Plain Text Editor",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net",
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    menu_actions = [
        (MENU_FILE, (
            ACTION_FILE_NEW, ACTION_FILE_OPEN, ACTION_FILE_SAVE, ACTION_FILE_SAVEAS, ACTION_FILE_CLOSE, ACTION_EXIT,
        )),
        (MENU_EDIT, (
            ACTION_EDIT_UNDO, ACTION_EDIT_REDO,
            ACTION_EDIT_CUT, ACTION_EDIT_COPY, ACTION_EDIT_PASTE,
            ACTION_EDIT_DELETE, ACTION_EDIT_SELECTALL, ACTION_EDIT_SELECTNONE, ACTION_EDIT_CLEAR,
            ACTION_EDIT_OVERWRITE,
        )),
        (MENU_HELP, (
            ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,
        )),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_NEW, ACTION_FILE_OPEN, ACTION_FILE_SAVE, ACTION_FILE_SAVEAS,),
        (ACTION_EDIT_UNDO, ACTION_EDIT_REDO,),
        (ACTION_EDIT_CUT, ACTION_EDIT_COPY, ACTION_EDIT_PASTE,),
        (ACTION_EDIT_DELETE, ACTION_EDIT_SELECTALL, ACTION_EDIT_SELECTNONE, ACTION_EDIT_CLEAR,),
        (ACTION_EDIT_OVERWRITE,),
        (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    status_labels = [
        ('overwrite', "", PANEL_SUNKEN),
        ('size', "0 bytes", PANEL_SUNKEN),
    ]
    
    main_title = "Plain Text Editor"
    main_iconfile = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                 "pnotepad.png")
    
    main_widget = memo('notepad', font=("Courier New", 12))
    
    def get_enable_list(self):
        actions = self.main_window.actions
        
        enable_list = [
            (getattr(self.memo_notepad, attr), actions[key].enable)
            for attr, key in (
                ('can_undo', ACTION_EDIT_UNDO),
                ('can_redo', ACTION_EDIT_REDO),
                ('can_clip', ACTION_EDIT_CUT),
                ('can_clip', ACTION_EDIT_COPY),
                ('can_paste', ACTION_EDIT_PASTE),
                ('can_clip', ACTION_EDIT_DELETE),
                ('can_clip', ACTION_EDIT_SELECTNONE),
            )
        ]
        
        dirty_list = [
            actions[key].enable
            for key in (
                ACTION_FILE_SAVE,
            )
        ]
        
        return enable_list, dirty_list
    
    def enable_actions(self, changed=None):
        for fstate, fenable in self.enable_list:
            fenable(fstate())
        # We have to check the changed parameter because the signal handler
        # for SIGNAL_TEXTCHANGED might be called before the one in the
        # PTextFile object that updates its dirty state
        dirty = changed if changed is not None else self.memo_file.dirty
        for fenable in self.dirty_list:
            fenable(dirty)
    
    filename_to_open = None
    file_not_found = False
    
    def check_file_open(self):
        if self.filename_to_open:
            filename = self.filename_to_open
            if os.path.isfile(filename):
                print("Opening", filename)
                self.memo_file.open_filename(filename)
            else:
                print(filename, "not found!")
                self.file_not_found = True
    
    def after_create(self):
        self.memo_file = PMemoFile(self, self.memo_notepad)
        self.enable_list, self.dirty_list = self.get_enable_list()
        self.enable_actions()
        self.update_filesize_status()
        self.update_overwrite_status()
        self.check_file_open()
    
    def set_status_text(self, text):
        print(text)
        self.main_window.statusbar.set_text(text)
    
    def update_filesize_status(self,
                               fmt="{} bytes".format):
        
        self.label_size.caption = fmt(self.memo_file.filesize)
    
    overwrite_labels = ("INS", "OVR")
    
    def update_overwrite_status(self):
        self.label_overwrite.caption = self.overwrite_labels[self.memo_notepad.overwrite_mode]
    
    def on_app_shown(self):
        if self.file_not_found:
            self.message_box.error("File Error", "File {} not found".format(self.filename_to_open))
    
    def on_notepad_changed(self):
        self.update_filesize_status()
    
    def on_notepad_mod_changed(self, changed):
        self.enable_actions(changed)
    
    def on_notepad_state_changed(self):
        self.enable_actions()
    
    def check_save(self):
        answer = self.message_box.query3(
            "Unsaved File",
            "Save file?"
        )
        return (
            True if answer == ANSWER_YES else
            False if answer == ANSWER_NO else
            None
        )
    
    def on_file_new(self):
        if self.memo_file.dirty:
            do_save = self.check_save()
            if do_save:
                self.memo_file.save_file()
            if do_save is None:
                return
        self.memo_file.new_file()
        self.enable_actions()
        self.set_status_text("New file")
        self.update_filesize_status()
    
    def on_file_open(self):
        if self.memo_file.open_file():
            self.enable_actions()
            self.set_status_text("Opened file: {}".format(self.memo_file.filename))
            self.update_filesize_status()
    
    def on_file_save(self):
        if self.memo_file.save_file():
            self.enable_actions()
            self.set_status_text("Saved file: {}".format(self.memo_file.filename))
    
    def on_file_saveas(self):
        if self.memo_file.save_file_as():
            self.enable_actions()
            self.set_status_text("Saved file: {}".format(self.memo_file.filename))
    
    def on_file_close(self):
        self.memo_file.close_file()
        self.update_filesize_status()
    
    def on_edit_undo(self):
        self.memo_notepad.undo_last()
        self.enable_actions()
    
    def on_edit_redo(self):
        self.memo_notepad.redo_last()
        self.enable_actions()
    
    def on_edit_cut(self):
        self.memo_notepad.cut_to_clipboard()
        self.enable_actions()
    
    def on_edit_copy(self):
        self.memo_notepad.copy_to_clipboard()
        self.enable_actions()
    
    def on_edit_paste(self):
        self.memo_notepad.paste_from_clipboard()
        self.enable_actions()
    
    def on_edit_delete(self):
        self.memo_notepad.delete_selected()
        self.enable_actions()
    
    def on_edit_selectall(self):
        self.memo_notepad.select_all()
        self.enable_actions()
    
    def on_edit_selectnone(self):
        self.memo_notepad.clear_selection()
        self.enable_actions()
    
    def on_edit_clear(self):
        self.memo_notepad.clear_edit()
        self.enable_actions()
    
    def on_edit_overwrite(self):
        # TODO: wx doesn't seem to support this? (the Ins key works, but no way to detect or control programmatically)
        self.memo_notepad.overwrite_mode = not self.memo_notepad.overwrite_mode
        self.update_overwrite_status()
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()
    
    def accept_close(self):
        if self.memo_file.dirty:
            do_save = self.check_save()
            if do_save:
                self.memo_file.save_file()
                return True
            if do_save is None:
                return False
            return self.message_box.query2(
                "Application Exit",
                "Exit anyway?"
            ) == ANSWER_OK
        return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PNotepad.filename_to_open = sys.argv[1]
    PNotepad().run()
