#!/usr/bin/env python3
"""
Module DISPLAY -- UI Text Display Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from .app import PWidgetBase


class PTextDisplayBase(PWidgetBase):
    """Base class for widget that displays multiple lines of text.
    """
    
    def __init__(self, manager, parent, text="",
                 scrolling=False, font=None):
        
        PWidgetBase.__init__(self, manager, parent,
                             font=font)
        self.setup_scrolling(scrolling)
        self.set_text(text)
    
    def setup_scrolling(self, scrolling):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_text(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_text(self, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def add_text(self, value):
        # This should be overridden in toolkits if possible
        data = "".join([self.get_text(), value])
        self.set_text(data)
    
    def clear_text(self):
        # This can be overridden in toolkits
        self.set_text("")
