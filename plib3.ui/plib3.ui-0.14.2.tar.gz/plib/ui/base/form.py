#!/usr/bin/env python3
"""
Module FORM -- UI Panel Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.defs import *
from plib.ui.widgets import widgets_from_contents

from .app import PWidgetBase


class PPanelBase(PWidgetBase):
    """Base class for 'panel' widget.
    
    The panel widget is a container for laying out
    other widgets. The layout parameter is used to
    determine whether child widgets are laid out
    horizontally or vertically; the align parameter
    determines how this panel takes up space in its
    parent widget. Panels should be nestable to any
    depth desired, to enable complex layouts.
    
    Note that there is currently no checking
    done to ensure that the align value of a panel
    makes sense when combined with the alignment of
    its sibling widgets and the layout of its parent
    widget (for example, an ALIGN_TOP or ALIGN_BOTTOM
    panel with ALIGN_LEFT or ALIGN_RIGHT siblings
    inside a LAYOUT_HORIZONTAL parent panel). It is
    up to the caller to ensure that the combined
    parameters make sense. (This also applies to the
    order in which child widgets are added -- for
    example, an ALIGN_LEFT widget must be added
    before an ALIGN_JUST widget in a horizontal
    layout, or the ALIGN_LEFT widget will be on the
    right.)
    """
    
    contents = None
    
    def __init__(self, manager, parent, align=ALIGN_JUST, layout=LAYOUT_NONE, contents=None,
                 style=PANEL_NONE, margin=None, spacing=None):
        
        PWidgetBase.__init__(self, manager, parent)
        
        self.layout = layout
        self.align = align
        self.style = style
        
        if (margin is not None):
            self.set_margin(margin)
        if (spacing is not None):
            self.set_spacing(spacing)
        
        # Create child panels, if any, and do layout if children were created
        self.create_contents(contents)
        self.do_layout()
    
    def add_widget(self, widget):
        # Derived classes may override to do any necessary
        # adjustment when a widget is added.
        pass
    
    def create_contents(self, contents):
        if self.contents is None:
            self.contents = []
        if contents:
            self.contents.extend(widgets_from_contents(self.manager, self, contents, self.add_widget))
    
    def do_layout(self):
        # Derived classes should override to do any
        # necessary creation of physical layout objects
        # after all child panels are created.
        pass
    
    def set_margin(self, margin):
        """Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_spacing(self, spacing):
        """Derived classes must implement.
        """
        raise NotImplementedError
