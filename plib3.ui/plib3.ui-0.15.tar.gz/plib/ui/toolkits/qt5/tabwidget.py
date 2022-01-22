#!/usr/bin/env python3
"""
Module QT5.TABWIDGET -- Python Qt 5 Tab Widget
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for the tab widget.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.tabwidget import PTabWidgetBase

from .app import PQtSequenceMeta, PQtWidgetBase


class PTabWidget(qt.QTabWidget, PQtWidgetBase, PTabWidgetBase,
                 metaclass=PQtSequenceMeta):
    
    widget_class = qt.QTabWidget
    
    def __init__(self, manager, parent, tabs=None):
        self._item = None
        self._target = None
        self._setting_index = False
        qt.QTabWidget.__init__(self, parent)
        PTabWidgetBase.__init__(self, manager, parent, tabs=tabs)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return PTabWidgetBase.count(self, value)
    
    def tab_count(self):
        # Let this method access the Qt tab widget count method.
        return qt.QTabWidget.count(self)
    
    def get_tab_title(self, index):
        return str(self.tabText(index))
    
    def set_tab_title(self, index, title):
        self.setTabText(index, str(title))
    
    def tab_at(self, index):
        return self.widget(index)
    
    def add_tab(self, index, title, widget):
        self.insertTab(index, widget, str(title))
    
    def del_tab(self, index):
        self.removeTab(index)
    
    def current_index(self):
        return self.currentIndex()
    
    def _current_changed(self, index):
        # Wrapper for tab changed signal.
        if (not self._setting_index) and self._target:
            self._target(index)
    
    def connect_target(self, signal, target):
        super_method = super(PTabWidget, self).connect_target
        if signal == SIGNAL_TABSELECTED:
            # Hack to capture double firing of tab changed signal when
            # tab is changed programmatically instead of by user
            self._target = target
            super_method(signal, self._current_changed)
        else:
            super_method(signal, target)
    
    def set_current_index(self, index):
        # Wrap the call to avoid double calling of signal handler, then
        # make the call by hand.
        self._setting_index = True
        self.setCurrentIndex(index)
        self._setting_index = False
        self._current_changed(index)
