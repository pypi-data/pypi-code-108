#!/usr/bin/env python3
"""
Module WX.LISTBOX -- Python wxWidgets List Box Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for the list box widgets.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.listbox import PListBoxBase, PSortedListBoxBase

from .app import PWxSequenceWidget


class PWxListBoxBase(PWxSequenceWidget, wx.ListBox):
    
    _align = False  # used by panel to determine placement
    _expand_horiz = True
    
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent,
                            style=(wx.LB_SINGLE | wx.LB_NEEDED_SB))
    
    #def item_height(self, index):
    #    return self.GetSizeFromText(self.GetString(index)).GetHeight()
    
    def item_text(self, item):
        return item  # items are the strings themselves
    
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


class PListBox(PWxListBoxBase, PListBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PWxListBoxBase.__init__(self, parent)
        PListBoxBase.__init__(self, manager, parent, items, value=value,
                              geometry=geometry)


class PSortedListBox(PWxListBoxBase, PSortedListBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None, key=None):
        
        PWxListBoxBase.__init__(self, parent)
        PSortedListBoxBase.__init__(self, manager, parent, items, value=value,
                                    geometry=geometry, key=key)
