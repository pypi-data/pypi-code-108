#!/usr/bin/env python3
"""
Module WX.DISPLAY -- Python wxWidgets Text Display Widgets
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for text display widgets.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.display import PTextDisplayBase

from .app import PWxWidget, ec_scroll_style


class PTextDisplay(PWxWidget, wx.TextCtrl, PTextDisplayBase):
    
    _style = wx.TE_MULTILINE | wx.TE_PROCESS_TAB | wx.TE_READONLY
    
    _align = True  # used by panel to determine placement
    _expand = True
    
    def __init__(self, manager, parent, text=None,
                 scrolling=False, font=None):
        
        if scrolling:
            self._style = self._style | ec_scroll_style
        wx.TextCtrl.__init__(self, parent, style=self._style)
        PTextDisplayBase.__init__(self, manager, parent, text,
                                  scrolling=scrolling, font=font)
    
    def setup_scrolling(self, scrolling):
        pass  # this must be done in the constructor in wxWidgets
    
    def get_text(self):
        return self.GetValue()
    
    def set_text(self, value):
        self.SetValue(value)
