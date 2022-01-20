#!/usr/bin/env python3
"""
Module CONTAINER -- UI Container Widget
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""


from .app import PWidgetBase


class PContainerBase(PWidgetBase):
    
    child = None
    
    def add_child(self, widget):
        if self.child:
            raise RuntimeError("Can't add more than one child to a container.")
        self.child = widget
        self.add_widget(widget)
        self.do_layout()
    
    def add_widget(self, widget):
        # Derived classes may override to do any necessary
        # adjustment when a widget is added.
        pass
    
    def do_layout(self):
        # Derived classes should override to do any
        # necessary creation of physical layout objects
        # after all child panels are created.
        pass
