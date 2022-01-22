#!/usr/bin/env python3
"""
Module PYSIDE2.CONTAINER-- Python PySide 2 Container Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for the panel widgets.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.container import PContainerBase

from .app import PQtWidget


class PContainer(PQtWidget, qt.QFrame, PContainerBase):
    
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
