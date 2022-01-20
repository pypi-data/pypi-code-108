#!/usr/bin/env python3
"""
Module OUTPUT-- UI Output Classes
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""


class PTextOutput(object):
    """File-like object to redirect output to text control.
    
    Note that 'file-like' is used very loosely; this object only
    implements the minimum necessary to make a PTextDisplay
    look like a bare bones file-like object. In particular,
    iterator functionality is *not* implemented.
    """
    
    def __init__(self, control):
        self.control = control  # should normally be a PTextDisplay
    
    def close(self):
        pass  # nothing to do here
    
    @property
    def filesize(self):
        return len(self.control.get_text())
    
    def truncate(self, size=None):
        if size is None:
            raise IOError("Must specify a size to truncate to (usually 0).")
        if size == 0:
            s = ""
        else:
            s = self.control.get_text()[:size]
        self.control.set_text(s)
        self.flush()
    
    def read(self):
        return self.control.get_text()
    
    def write(self, data):
        self.control.add_text(data)
    
    def flush(self):
        self.control.update_widget()
    
    def clear(self):
        self.control.clear_text()
