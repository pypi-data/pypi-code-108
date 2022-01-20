#!/usr/bin/env python3
"""
Module WX.COMBO -- Python wxWidgets Combo Box Widgets
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for combo boxes.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.combo import PComboBoxBase, PNumComboBoxBase, PSortedComboBoxBase

from .app import PWxSequenceWidget


class PWxComboBoxBase(PWxSequenceWidget, wx.ComboBox):
    
    _align = False  # used by panel to determine placement
    _expand_horiz = True
    
    def __init__(self, parent):
        wx.ComboBox.__init__(self, parent,
                             style=(wx.CB_DROPDOWN | wx.CB_READONLY))
    
    def current_text(self):
        return self.GetStringSelection()
    
    def set_current_text(self, text):
        self.SetStringSelection(text)
    
    def current_index(self):
        return self.GetSelection()
    
    def set_current_index(self, index):
        self.SetSelection(index)
    
    def _indexlen(self):
        return self.GetCount()
    
    def _get_data(self, index):
        return self.GetString(index)
    
    def _set_data(self, index, value):
        self.SetString(index, value)
    
    def _add_data(self, index, value):
        if index == self.__len__():
            self.Append(value)
        else:
            self.Insert(value, index)
    
    def _del_data(self, index):
        self.Delete(index)


class PComboBox(PWxComboBoxBase, PComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PWxComboBoxBase.__init__(self, parent)
        PComboBoxBase.__init__(self, manager, parent, items, value=value,
                               geometry=geometry)


class PNumComboBox(PWxComboBoxBase, PNumComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PWxComboBoxBase.__init__(self, parent)
        PNumComboBoxBase.__init__(self, manager, parent, items, value=value,
                                  geometry=geometry)


class PSortedComboBox(PWxComboBoxBase, PSortedComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None, key=None):
        
        PWxComboBoxBase.__init__(self, parent)
        PSortedComboBoxBase.__init__(self, manager, parent, items, value=value,
                                     geometry=geometry, key=key)
