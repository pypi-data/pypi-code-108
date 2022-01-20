#!/usr/bin/env python3
"""
Module QT5.CONTAINER-- Python Qt 5 Container Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for the panel widgets.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.base.container import PContainerBase

from .app import PQtWidgetBase


class PContainer(qt.QFrame, PQtWidgetBase, PContainerBase):
    
    def __init__(self, manager, parent):
        qt.QFrame.__init__(self, parent)
        self.setFrameStyle(qt.QFrame.NoFrame | qt.QFrame.Plain)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        self._playout = qt.QVBoxLayout()
        PContainerBase.__init__(self, manager, parent)
    
    def add_widget(self, widget):
        self._playout.addWidget(widget)
    
    def do_layout(self):
        #self._playout.addStretch(1)
        self.setLayout(self._playout)
