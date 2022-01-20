#!/usr/bin/env python3
"""
Module WX.GROUPBOX -- Python wxWidgets Group Box Widgets
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for group box widgets.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.groupbox import PGroupBoxBase

from .app import PWxWidget


class PGroupBox(PWxWidget, wx.Panel, PGroupBoxBase):
    
    _align = False  # used by panel to determine placement
    _expand_horiz = True
    
    def __init__(self, manager, parent, caption, contents=None,
                 geometry=None, margin=None, spacing=None):
        
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self._margin = margin
        self._spacing = spacing
        self._haswidgets = False
        self._box = wx.StaticBox(self)
        self._boxsizer = wx.StaticBoxSizer(self._box, wx.VERTICAL)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self._boxsizer, 1, wx.EXPAND, 0)
        PGroupBoxBase.__init__(self, manager, parent, caption, contents,
                               geometry=geometry, margin=margin, spacing=spacing)
    
    def set_caption(self, caption):
        self._box.SetLabel(caption)
    
    def set_min_size(self, width, height):
        self._sizer.SetMinSize((width, height))
    
    def set_margin(self, margin):
        # Margin is dealt with differently in wxWidgets, see above
        pass
    
    def set_spacing(self, spacing):
        # Spacing is dealt with differently in wxWidgets, see above
        pass
    
    def add_control(self, control):
        # Somewhat abbreviated version of the cruft in PPanel
        
        if self._haswidgets:
            if self._spacing is not None:
                self._boxsizer.AddSpacer(self._spacing)
        elif self._margin is not None:
            self._boxsizer.AddSpacer(self._margin)
        
        if getattr(control, '_align', None):
            proportion = 1
        else:
            proportion = 0
        
        if getattr(control, '_expand', None) or getattr(control, '_expand_horiz', None):
            flag = wx.EXPAND
        else:
            flag = 0
        
        flag |= wx.LEFT | wx.RIGHT
        border = self._margin or 0
        
        self._boxsizer.Add(control, proportion, flag, border)
        if not self._haswidgets:
            self._haswidgets = True
    
    def do_layout(self):
        if self._margin is not None:
            self._boxsizer.AddSpacer(self._margin)
        self.SetSizerAndFit(self._sizer)
