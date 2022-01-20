#!/usr/bin/env python3
"""
Module DIALOG -- UI Button Widget
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.defs import *
from plib.ui.widgets import widget_from_spec

from .app import PWidgetBase


class PDialogBase(PWidgetBase):
    """Base class for dialogs.
    """
    
    control_widget = None
    
    def __init__(self, manager, parent, caption, client=None,
                 accept_buttons=('ok', 'yes'), reject_buttons=('cancel', 'no')):
        
        PWidgetBase.__init__(self, manager, parent)
        self.set_caption(caption)
        self.create_controls(client)
        self.size_to_controls(*self.get_controls_size())
        for button in accept_buttons:
            self.setup_button(button, self.accept_changes)
        for button in reject_buttons:
            self.setup_button(button, self.reject_changes)
    
    def setup_button(self, button, method):
        control = getattr(self.manager, 'button_{}'.format(button), None)
        if control:
            for sig in control.signals:
                control.setup_notify(sig, method)
    
    def get_controls_size(self):
        """Return tuple of (width, height) needed to wrap client.
        """
        c = self.control_widget
        return (c.preferred_width(), c.preferred_height())
    
    def create_controls(self, client):
        # The dialog itself has no layout capabilities, so there can
        # only be a single client: normally a panel or group box, so
        # the actual controls and layout are handled by the client
        self.control_widget = widget_from_spec(self.manager, self, *client)
    
    def size_to_controls(self, width, height):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def display(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def accept_changes(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def reject_changes(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
