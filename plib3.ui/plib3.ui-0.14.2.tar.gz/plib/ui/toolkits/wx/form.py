#!/usr/bin/env python3
"""
Module WX.FORM -- Python wxWidgets Panel Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for the panel widgets.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.form import PPanelBase

from .app import PWxWidget


wx_styles = {
    PANEL_NONE: wx.NO_BORDER,
    PANEL_BOX: wx.SIMPLE_BORDER,
    PANEL_RAISED: wx.RAISED_BORDER,
    PANEL_SUNKEN: wx.SUNKEN_BORDER
}

wx_layouts = {
    LAYOUT_NONE: wx.HORIZONTAL,
    LAYOUT_HORIZONTAL: wx.HORIZONTAL,
    LAYOUT_VERTICAL: wx.VERTICAL
}


class PPanel(PWxWidget, wx.Panel, PPanelBase):
    
    _expand = True  # used by parent panel to determine placement
    
    def __init__(self, manager, parent, align=ALIGN_JUST, layout=LAYOUT_NONE, contents=None,
                 style=PANEL_NONE, margin=None, spacing=None):
        
        wx.Panel.__init__(self, parent, style=wx_styles[style])
        self._align = (align == ALIGN_JUST)
        self._margin = margin
        self._spacing = spacing
        self._haswidgets = False
        self._sizer = wx.BoxSizer(wx_layouts[layout])
        PPanelBase.__init__(self, manager, parent, align, layout, contents=contents,
                            style=style, margin=margin, spacing=spacing)
    
    def set_min_size(self, width, height):
        self._sizer.SetMinSize((width, height))
    
    def set_margin(self, margin):
        # Margin is dealt with differently in wxWidgets, see above
        pass
    
    def set_spacing(self, spacing):
        # Spacing is dealt with differently in wxWidgets, see above
        pass
    
    def add_widget(self, widget):
        # People say the wxWidgets layout model is simple and easy to use,
        # but comparing this cruft with the PySide/Qt code, I'm not so sure...
        
        if self._haswidgets:
            if self._spacing is not None:
                self._sizer.AddSpacer(self._spacing)
        elif self._margin is not None:
            self._sizer.AddSpacer(self._margin)
        
        if getattr(widget, '_align', None):
            proportion = 1
        else:
            proportion = 0
        
        if getattr(widget, '_expand', None):
            flag = wx.EXPAND
        else:
            flag = 0
        
        exp = getattr(widget, '_expand_horiz', None)
        if self._sizer.GetOrientation() == wx.VERTICAL:
            horiz_pad = self._margin or 0
            vert_pad = None
            if exp:
                flag |= wx.EXPAND
        else:
            horiz_pad = None
            vert_pad = self._margin or 0
            if exp:
                proportion = 1
        
        if horiz_pad is not None:
            flag |= wx.LEFT | wx.RIGHT
            border = horiz_pad
        elif vert_pad is not None:
            flag |= wx.TOP | wx.BOTTOM
            border = vert_pad
        else:
            border = 0
        
        # At last we can actually do what we came for...
        self._sizer.Add(widget, proportion, flag, border)
        if not self._haswidgets:
            self._haswidgets = True
    
    def do_layout(self):
        if self._margin is not None:
            self._sizer.AddSpacer(self._margin)
        self.SetSizerAndFit(self._sizer)
