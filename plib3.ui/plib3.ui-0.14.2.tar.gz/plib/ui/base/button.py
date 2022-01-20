#!/usr/bin/env python3
"""
Module BUTTON -- UI Button Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.defs import *

from .app import PActionMixin, PWidgetBase


class PButtonBase(PActionMixin, PWidgetBase):
    """Base class for push button.
    """
    
    signals = (
        SIGNAL_CLICKED,
    )
    
    def __init__(self, manager, parent, caption, icon=None,
                 geometry=None):
        
        if caption:
            self.set_caption(caption)
        if icon:
            self.set_icon(icon)
        PWidgetBase.__init__(self, manager, parent,
                             geometry=geometry)
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_icon_obj(self, icon):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_icon(self, icon):
        if isinstance(icon, int):
            # Assume it's an action key
            icon = self.get_icon(icon)
        elif isinstance(icon, str):
            # Assume its an image filename
            icon = self.load_icon_from_file(icon)
        # At this point it should be an icon object
        self.set_icon_obj(icon)


class PActionButtonBase(PButtonBase):
    
    signals = (
        SIGNAL_ACTIVATED,
    )
    
    def __init__(self, manager, parent, action,
                 geometry=None):
        
        # These checks allow toolkits to override the captions and icons
        # by passing a zero or negative action key
        caption = self.get_menu_str(action) if (action or -1) > 0 else None
        icon = self.get_icon(action) if (action or -1) > 0 else None
        PButtonBase.__init__(self, manager, parent, caption, icon,
                             geometry=geometry)
        
        # Convert click events to activated events
        self.setup_notify(SIGNAL_CLICKED, self.activate)
    
    def activate(self):
        self.do_notify(SIGNAL_ACTIVATED)


class PCheckBoxBase(PButtonBase):
    """ Base class for checkbox.
    """
    
    signals = (
        SIGNAL_TOGGLED,
    )
    
    fn_get_checked = None
    fn_set_checked = None
    
    def __init__(self, manager, parent, label, checked=None,
                 geometry=None, tristate=False):
        
        PButtonBase.__init__(self, manager, parent, label,
                             geometry=geometry)
        if tristate:
            self.make_tristate()
        if checked is not None:
            self.checked = checked
    
    def make_tristate(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_checked(self):
        return getattr(self, self.fn_get_checked)()
    
    def set_checked(self, value):
        getattr(self, self.fn_set_checked)(value)
    
    checked = property(get_checked, set_checked)
    
    def set_icon(self, icon):
        # No icons on checkboxes
        pass
