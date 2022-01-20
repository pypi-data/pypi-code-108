#!/usr/bin/env python3
"""
Module EDITCTRL -- UI Editing Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import functools

from plib.ui.defs import *

from .app import PWidgetBase


class PEditBase(PWidgetBase):
    """Base edit control class, defines standard API.
    """
    
    fn_get_text = None
    fn_set_text = None
    
    fn_get_read_only = None
    fn_set_read_only = None
    
    def get_text(self):
        return getattr(self, self.fn_get_text)()
    
    def set_text(self, value):
        getattr(self, self.fn_set_text)(value)
    
    edit_text = property(get_text, set_text)
    
    def get_read_only(self):
        return getattr(self, self.fn_get_read_only)()
    
    def set_read_only(self, value):
        getattr(self, self.fn_set_read_only)(value)
    
    read_only = property(get_read_only, set_read_only)


class PEditBoxBase(PEditBase):
    """Base class for single-line input control.
    """
    
    signals = (
        SIGNAL_EDITCHANGED,
        SIGNAL_ENTER,
    )
    
    def __init__(self, manager, parent, text="",
                 geometry=None, expand=True):
        
        self.setup_expand(expand)  # needs to be done before geometry is set
        PEditBase.__init__(self, manager, parent,
                           geometry=geometry)
        self.edit_text = text
    
    def setup_expand(self, expand):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PNumEditBoxBase(PEditBoxBase):
    """Base class for edit box for editing numbers.
    """
    
    def __init__(self, manager, parent, value=0,
                 geometry=None, expand=True):
        
        PEditBoxBase.__init__(self, manager, parent,
                              geometry=geometry, expand=expand)
        self.set_value(value)
    
    def get_value(self):
        return int(self.get_text())
    
    def set_value(self, value):
        if not isinstance(value, int):
            raise TypeError("Numeric edit can only accept int values: {} is not an int".format(repr(value)))
        self.set_text(str(value))
    
    edit_value = property(get_value, set_value)
    
    def wrap_target(self, signal, target):
        if signal == SIGNAL_EDITCHANGED:
            @functools.wraps(target)
            def _wrapper(text):
                target(int(text))
            return _wrapper
        return target


class PEditControlBase(PEditBase):
    """Base class for multi-line edit control.
    """
    
    signals = (
        SIGNAL_TEXTCHANGED,
        SIGNAL_TEXTMODCHANGED,
        SIGNAL_TEXTSTATECHANGED,
    )
    
    def __init__(self, manager, parent, text="",
                 scrolling=False, font=None):
        
        PEditBase.__init__(self, manager, parent,
                           font=font)
        self.setup_scrolling(scrolling)
        self.edit_text = text
    
    fn_get_overwrite = None
    fn_set_overwrite = None
    
    def get_overwrite_mode(self):
        return getattr(self, self.fn_get_overwrite)()
    
    def set_overwrite_mode(self, value):
        getattr(self, self.fn_set_overwrite)(value)
    
    overwrite_mode = property(get_overwrite_mode, set_overwrite_mode)
    
    def setup_scrolling(self, scrolling):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_undo(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_redo(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_clip(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_paste(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def clear_edit(self):
        # Derived classes may implement a faster method
        self.edit_text = ""
    
    def undo_last(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def redo_last(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def select_all(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def delete_selected(self):
        self.cut_to_clipboard()
        self.delete_last_cut()
    
    def clear_selection(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def copy_to_clipboard(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def cut_to_clipboard(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def delete_last_cut(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def paste_from_clipboard(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
