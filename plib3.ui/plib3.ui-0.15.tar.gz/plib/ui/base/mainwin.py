#!/usr/bin/env python3
"""
Module MAINWIN -- UI Main Window Classes
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the classes for fully functional decorated GUI main
windows. This module is kept separate from the ``app`` module
so that applications that do not require a full main window
but just a "bare" top window do not have to import any code
that is only used with a full main window.
"""

from plib.ui.defs import *
from plib.ui.common import *
from plib.ui.widgets import setup_signal_handlers, widget_from_spec

from .app import PSignalBase, PActionMixin, PTopWindowBase


class PUIBase(object):
    """Base class for UI menus and toolbars.
    """
    
    def __init__(self, main_window):
        self.main_window = main_window


class PMenuBase(PUIBase):
    """Base class for UI menu.
    """
    
    popup_class = None
    
    popups = None
    
    def store_popup(self, title, popup):
        if self.popups is None:
            self.popups = {}
        self.popups[title] = popup
    
    def do_add_popup(self, title, popup):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def add_popup(self, title):
        popup = self.popup_class(self.main_window)
        self.do_add_popup(title, popup)
        self.store_popup(title, popup)
        return popup
    
    def get_popup(self, title):
        return self.popups.get(title) if self.popups else None
    
    def add_popup_action(self, action, popup):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PToolBarBase(PUIBase):
    """Base class for UI toolbar.
    """
    
    def add_action(self, action):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def add_separator(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PStatusLabelBase(object):
    """Base class for status bar labels.
    """
    
    actual_widget = None
    
    def __init__(self, manager, parent, caption="", style=PANEL_NONE):
        self._manager = manager
        self._parent = parent
        self._caption = caption
        self._style = style
        self.init_status_label()
    
    def init_status_label(self):
        raise NotImplementedError
    
    fn_get_text = None
    fn_set_text = None
    
    def get_text(self):
        return getattr(self, self.fn_get_text)()
    
    def set_text(self, value):
        getattr(self, self.fn_set_text)(value)
    
    caption = property(get_text, set_text)


class PStatusBarBase(object):
    """Base class for UI status bar.
    
    A standard status bar with a text area on the left and an
    area for custom widgets on the right.
    """
    
    text_area_class = None
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.create_text_area()
        self.create_widgets()
    
    def add_widget(self, widget, expand=False, custom=True):
        """Placeholder for derived classes to implement
        """
        raise NotImplementedError
    
    def create_widgets(self,
                       kwargs={}):
        
        app = self.main_window.app
        labels = app.status_labels
        if labels is not None:
            for label_spec in labels:
                name, *args = label_spec
                label = widget_from_spec(app, self, 'mainwin', 'PStatusLabel', name, args, kwargs)
                self.add_widget(label.actual_widget)
    
    def create_text_area(self):
        self.text_area = None
        if self.text_area_class is not None:
            self.text_area = self.text_area_class(self.main_window.app, self)
            # This should be the only widget added with expand=True and custom=False
            self.add_widget(self.text_area, True, False)
    
    def get_text(self):
        return self.text_area.get_text()
    
    def set_text(self, value):
        self.text_area.set_text(value)


class PActionBase(PActionMixin, PSignalBase):
    """Base class for UI action objects.
    """
    
    signals = (
        SIGNAL_ACTIVATED,
    )
    
    def __init__(self, key, main_window):
        self.key = key
        self.main_window = main_window
    
    def enable(self, enabled):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PMainWindowBase(PTopWindowBase):
    """Base class for 'main window' widgets.
    
    The main window is a fancier version of the top window, which
    includes all the frills that PTopWindow leaves out.
    """
    
    menu_class = None
    toolbar_class = None
    statusbar_class = None
    action_class = None
    
    actions = None
    
    def before_client(self):
        self.menu = self.create_menu() if self.app.include_menu else None
        self.toolbar = self.create_toolbar() if self.app.include_toolbar else None
        self.statusbar = self.create_statusbar() if self.app.include_statusbar else None
        
        self.actions = self.create_actions()
    
    def create_menu(self):
        """Create the main window's menu.
        """
        return self.menu_class(self)
    
    def create_toolbar(self):
        """Create the main window's toolbar.
        """
        return self.toolbar_class(self)
    
    def create_statusbar(self):
        """Create the main window's status bar.
        """
        return self.statusbar_class(self)
    
    def action_exists(self, key):
        """Return True if action key is in our list of actions.
        """
        return (key in self.app.action_flags)
    
    def create_action(self, key):
        """Return an action object for key.
        """
        return self.action_class(key, self)
    
    def get_action(self, actions, key):
        action = actions.get(key)
        if not action:
            actions[key] = action = self.create_action(key)
            setup_signal_handlers(self.app, action, action_name(key))
        return action
    
    def create_actions(self):
        """Create actions and link them to menu and toolbar items.
        """
        
        actions = {}
        
        for title, action_list in (self.app.menu_actions or ()):
            popup = self.menu.add_popup(title)
            for key in action_list:
                action = self.get_action(actions, key)
                self.menu.add_popup_action(action, popup)
        
        toolbar_started = False
        for action_list in (self.app.toolbar_actions or ()):
            if toolbar_started:
                self.toolbar.add_separator()
            else:
                toolbar_started = True
            for key in action_list:
                action = self.get_action(actions, key)
                self.toolbar.add_action(action)
        
        return actions
    
    def update_action(self, key, flag):
        """Update action enable state based on flag.
        """
        
        if self.action_exists(key):
            self.actions[key].enable(flag)
    
    def menu_height(self):
        return self.menu.preferred_height()
    
    def toolbar_height(self):
        return self.toolbar.preferred_height()
    
    def statusbar_height(self):
        return self.statusbar.preferred_height()
    
    def get_client_size(self):
        h = self.client_widget.preferred_height()
        if self.menu is not None:
            h += self.menu_height()
        if self.toolbar is not None:
            h += self.toolbar_height()
        if self.statusbar is not None:
            h += self.statusbar_height()
        w = 0
        for widget in (self.client_widget, self.toolbar):
            w = max(w, widget.preferred_width())
        return (w, h)
