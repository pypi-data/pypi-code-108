#!/usr/bin/env python3
"""
Module WX.LABEL -- Python wxWidgets Text Label Widgets
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for text label widgets.
"""

import wx

from plib.ui.defs import *
from plib.ui.base.label import PTextLabelBase

from .app import PWxWidget


class PTextLabel(PWxWidget, wx.StaticText, PTextLabelBase):
    
    _align = False  # used by panel to determine placement
    
    def __init__(self, manager, parent, text=None,
                 geometry=None, font=None):
        
        wx.StaticText.__init__(self, parent)
        PTextLabelBase.__init__(self, manager, parent, text,
                                geometry=geometry, font=font)
    
    fn_get_text = 'GetLabel'
    fn_set_text = 'SetLabel'
