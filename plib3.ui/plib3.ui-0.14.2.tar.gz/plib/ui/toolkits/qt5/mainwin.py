#!/usr/bin/env python3
"""
Module QT5.MAINWIN -- Python Qt 5 Main Window Objects
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI main window objects. It is kept
separate from the ``app`` module so that applications that do not
require a full main window but just a "bare" top window do not have
to import any code that is only used with a full main window.
"""

from PyQt5 import QtCore as qtc, QtGui as qtg, QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.mainwin import PMenuBase, PToolBarBase, PStatusLabelBase, PStatusBarBase, PActionBase, PMainWindowBase

from .app import PQtWidgetMeta, PQtSignalBase, PQtActionMixin, PQtWidgetBase, PTopWindow
from .form import PPanel
from .label import PTextLabel


class PQtMenu(qt.QMenuBar, PQtWidgetBase, PMenuBase):
    """Customized Qt menu class.
    """
    
    widget_class = qt.QMenuBar
    
    popup_class = qt.QMenu
    
    def __init__(self, main_window):
        qt.QMenuBar.__init__(self, main_window)
        PMenuBase.__init__(self, main_window)
        main_window.setMenuBar(self)
    
    def do_add_popup(self, title, popup):
        popup.setTitle(title)
        self.addMenu(popup)
    
    def add_popup_action(self, action, popup):
        popup.addAction(action)


class PQtToolBar(qt.QToolBar, PQtWidgetBase, PToolBarBase):
    """Customized Qt toolbar class.
    """
    
    widget_class = qt.QToolBar
    
    def __init__(self, main_window):
        qt.QToolBar.__init__(self, main_window)
        if main_window.app.large_icons:
            sz = self.iconSize()
            self.setIconSize(qtc.QSize(
                *[i * 3 / 2 for i in (sz.width(), sz.height())]))
        if main_window.app.show_labels:
            style = qtc.Qt.ToolButtonTextUnderIcon
        else:
            style = qtc.Qt.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        PToolBarBase.__init__(self, main_window)
        main_window.addToolBar(self)
    
    def add_action(self, action):
        self.addAction(action)
    
    def add_separator(self):
        self.addSeparator()


class PQtStatusPanel(PPanel):
    
    label = None
    
    def __init__(self, manager, parent, caption="", style=PANEL_NONE):
        PPanel.__init__(self, manager, parent, ALIGN_RIGHT, LAYOUT_HORIZONTAL,
                        style=style, margin=PANEL_MARGIN, spacing=PANEL_SPACING)
        self.label = PTextLabel(manager, self, caption)
        self.add_widget(self.label)
        self.do_layout()
    
    def create_contents(self, contents):
        assert not contents  # we will create our label manually, not using specs
    
    def do_layout(self):
        # This ensures that we only do the layout
        if self.label:
            super(PQtStatusPanel, self).do_layout()


class PStatusLabel(PStatusLabelBase):
    
    def init_status_label(self):
        self.panel = PQtStatusPanel(self._manager, self._parent, caption=self._caption, style=self._style)
        self.label = self.panel.label
        self.actual_widget = self.panel
        
        self.text = self.label.text
        self.setText = self.label.setText
    
    fn_get_text = 'text'
    fn_set_text = 'setText'


class PQtStatusBar(qt.QStatusBar, PQtWidgetBase, PStatusBarBase):
    
    widget_class = qt.QStatusBar
    
    text_area_class = PTextLabel
    
    def __init__(self, main_window):
        qt.QStatusBar.__init__(self, main_window)
        PStatusBarBase.__init__(self, main_window)
        main_window.setStatusBar(self)
    
    def add_widget(self, widget, expand=False, custom=True):
        if custom:
            self.addPermanentWidget(widget, int(expand))
        else:
            self.addWidget(widget, int(expand))


class PQtAction(qt.QAction, PQtActionMixin, PQtSignalBase, PActionBase):
    """Customized Qt action class.
    """
    
    def __init__(self, key, main_window):
        qt.QAction.__init__(self, main_window)
        self.setIcon(self.get_icon(key))
        self.setText(self.get_menu_str(key))
        self.setToolTip(self.get_toolbar_str(key))
        self.setStatusTip(self.get_statusbar_str(key))
        s = self.get_accel_str(key)
        if s is not None:
            if isinstance(s, str):
                self.setShortcut(qtg.QKeySequence(s))
            elif isinstance(s, qtg.QKeySequence.StandardKey):
                self.setShortcuts(qtg.QKeySequence.keyBindings(s))
        PActionBase.__init__(self, key, main_window)
    
    def enable(self, enabled):
        self.setEnabled(enabled)


class PMainWindow(PTopWindow, PMainWindowBase,
                  metaclass=PQtWidgetMeta):
    """Customized Qt main window class.
    """
    
    menu_class = PQtMenu
    toolbar_class = PQtToolBar
    statusbar_class = PQtStatusBar
    action_class = PQtAction
