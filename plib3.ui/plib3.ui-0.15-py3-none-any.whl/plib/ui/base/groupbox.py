#!/usr/bin/env python3
"""
Module GROUPBOX -- UI Group Box Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.widgets import widgets_from_contents

from .app import PWidgetBase


class PGroupBoxBase(PWidgetBase):
    """Base class for group box widget.
    """
    
    controls = None
    
    def __init__(self, manager, parent, caption, contents=None,
                 geometry=None, margin=None, spacing=None):
        
        PWidgetBase.__init__(self, manager, parent,
                             geometry=geometry)
        
        self.set_caption(caption)
        if (margin is not None):
            self.set_margin(margin)
        if (spacing is not None):
            self.set_spacing(spacing)
        self.init_controls(contents)
        self.do_layout()
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_margin(self, margin):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_spacing(self, spacing):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def init_controls(self, contents):
        if self.controls is None:
            self.controls = []
        self.controls.extend(widgets_from_contents(self.manager, self, contents, self.add_control))
    
    def add_control(self, control):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def do_layout(self):
        # Derived classes should override to do any
        # necessary creation of physical layout objects
        # after all child controls are created.
        pass
