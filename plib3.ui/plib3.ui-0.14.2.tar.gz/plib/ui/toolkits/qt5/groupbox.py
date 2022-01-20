#!/usr/bin/env python3
"""
Module QT5.GROUPBOX -- Python Qt 5 Group Box Widgets
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for group box widgets.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.base.groupbox import PGroupBoxBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PGroupBox(qt.QGroupBox, PQtWidgetBase, PGroupBoxBase,
                metaclass=PQtWidgetMeta):
    
    widget_class = qt.QGroupBox
    
    def __init__(self, manager, parent, caption, contents=None,
                 geometry=None, margin=None, spacing=None):
        
        qt.QGroupBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding,
                           qt.QSizePolicy.Fixed)
        self._vlayout = qt.QVBoxLayout()
        PGroupBoxBase.__init__(self, manager, parent, caption, contents,
                               geometry=geometry, margin=margin, spacing=spacing)
    
    def set_caption(self, caption):
        self.setTitle(caption)
    
    def set_margin(self, margin):
        self._vlayout.setContentsMargins(margin, margin, margin, margin)
    
    def set_spacing(self, spacing):
        self._vlayout.setSpacing(spacing)
    
    def add_control(self, control):
        self._vlayout.addWidget(control)
    
    def do_layout(self):
        self._vlayout.addStretch(1)
        self.setLayout(self._vlayout)
