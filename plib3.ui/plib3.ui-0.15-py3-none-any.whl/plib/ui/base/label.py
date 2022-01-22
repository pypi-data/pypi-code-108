#!/usr/bin/env python3
"""
Module LABEL -- UI Text Label Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from .app import PWidgetBase


class PTextLabelBase(PWidgetBase):
    """Base class for widget that displays a single line of text.
    """
    
    def __init__(self, manager, parent, caption="",
                 geometry=None, font=None):
        
        PWidgetBase.__init__(self, manager, parent,
                             geometry=geometry, font=font)
        self.caption = caption
    
    fn_get_text = None
    fn_set_text = None
    
    def get_text(self):
        return getattr(self, self.fn_get_text)()
    
    def set_text(self, value):
        getattr(self, self.fn_set_text)(value)
    
    caption = property(get_text, set_text)
