#!/usr/bin/env python3
"""
Module WX.TABWIDGET -- Python wxWidgets Tab Widget
Sub-Package UI.TOOLKITS.QT of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for the tab widget.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.tabwidget import PTabWidgetBase

from .app import PWxSequenceWidget


class PTabWidget(PWxSequenceWidget, wx.Notebook, PTabWidgetBase):
    
    _align = True  # used by panel to determine placement
    _expand = True
    
    def __init__(self, manager, parent, tabs=None):
        wx.Notebook.__init__(self, parent)
        PTabWidgetBase.__init__(self, manager, parent, tabs=tabs)
    
    def tab_count(self):
        return self.GetPageCount()
    
    def get_tab_title(self, index):
        return self.GetPageText(index)
    
    def set_tab_title(self, index, title):
        self.SetPageText(index, title)
    
    def tab_at(self, index):
        return self.GetPage(index)
    
    def add_tab(self, index, title, widget):
        if index == self.__len__():
            self.AddPage(widget, title)
        else:
            self.InsertPage(index, widget, title)
    
    def del_tab(self, index):
        self.RemovePage(index)
    
    def current_index(self):
        return self.GetSelection()
    
    def set_current_index(self, index):
        self.SetSelection(index)
