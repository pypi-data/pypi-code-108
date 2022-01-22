#!/usr/bin/env python3
"""
Module TEXTFILE -- UI File-Aware Text Control Helper
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import os

from plib.ui.defs import *
from plib.ui.fileaware import PFileAware


class PTextFile(PFileAware):
    """Make a text edit control file-aware.
    """
    
    def __init__(self, app, control, filter=None, filter_index=0, file_path=None, update_filter=True, update_index=0, update_path=True):
        PFileAware.__init__(self, app, filter, filter_index, file_path, update_filter, update_index, update_path)
        self.control = control  # should normally be a PEditControl
        self.dirty = False
        
        # So we can keep track of "dirty" state
        control.setup_notify(SIGNAL_TEXTMODCHANGED, self.editor_changed)
    
    @property
    def filesize(self):
        return len(self.control.edit_text)
    
    def new_file(self):
        super(PTextFile, self).new_file()
        self.set_filename(self.untitled)
    
    def open_data(self, filename):
        with open(filename, 'r') as f:
            data = f.read()
        self.control.edit_text = data
        self.dirty = False
    
    def editor_changed(self, changed):
        self.dirty = changed
    
    def save_data(self, filename):
        data = self.control.edit_text
        with open(filename, 'w') as f:
            f.write(data)
        self.dirty = False
    
    def filename_unknown(self):
        return (not self.filename) or (self.filename is self.untitled)
    
    def close_file(self):
        # Calling application must make sure data is saved first
        self.control.clear_edit()
        self.dirty = False
        super(PTextFile, self).close_file()
