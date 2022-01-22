#!/usr/bin/env python3
"""
Module FILEAWARE -- UI File-Aware Base Class
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import os


class PFileAware(object):
    """Base functionality for file-aware control or application.
    """
    
    def __init__(self, app, filter=None, filter_index=0, file_path=None, update_filter=True, update_index=0, update_path=True):
        self.app = app
        self.file_filter = filter
        self.filter_index = filter_index
        self.filename = None
        self.file_path = file_path or os.curdir
        self.update_filter = update_filter
        self.update_index = update_index
        self.update_path = update_path
    
    @property
    def selected_filter(self):
        return self.file_filter[self.filter_index] if self.file_filter else None
    
    @property
    def known_extensions(self):
        return set(ext for caption, ext_list in self.file_filter for ext in ext_list)
    
    def caption_from_ext(self, ext):
        return "{} Files".format(ext.upper())
    
    def add_extension(self, ext, update_index=None):
        if update_index is None:
            self.file_filter.append((self.caption_from_ext(ext), [ext]))
        else:
            self.file_filter[update_index][1].append(ext)
    
    def filename_unknown(self):
        return not self.filename
    
    def set_filename(self, filename):
        self.filename = filename
        if self.filename_unknown():
            return
        if self.update_filter:
            ext = os.path.splitext(filename)[-1]
            if ext:
                ext = ext.lstrip(".")
                if ext not in self.known_extensions:
                    self.add_extension(ext, self.update_index)
        if self.update_path:
            self.file_path = os.path.dirname(filename)
    
    def new_file(self):
        self.close_file()
    
    def open_data(self, filename):
        # Must be implemented by subclass
        raise NotImplementedError
    
    def open_filename(self, filename):
        self.set_filename(filename)
        self.open_data(filename)
    
    def open_file(self):
        filename = self.app.file_dialog.open_filename(self.file_path, self.file_filter, self.selected_filter)
        if filename:
            self.open_filename(filename)
            return True
        return False
    
    def save_data(self, filename):
        # Must be implemented by subclass
        raise NotImplementedError
    
    def save_filename(self, filename):
        self.set_filename(filename)
        self.save_data(filename)
    
    def save_file_as(self):
        filename = self.app.file_dialog.save_filename(self.file_path, self.file_filter, self.selected_filter)
        if filename:
            self.save_filename(filename)
            return True
        return False
    
    def save_file(self):
        if self.filename_unknown():
            return self.save_file_as()
        else:
            self.save_data(self.filename)
            return True
    
    def close_file(self):
        self.set_filename(None)
