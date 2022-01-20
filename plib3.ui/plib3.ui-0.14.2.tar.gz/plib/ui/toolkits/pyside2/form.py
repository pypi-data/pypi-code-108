#!/usr/bin/env python3
"""
Module PYSIDE2.FORM -- Python PySide 2 Panel Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for the panel widgets.
"""

from PySide2 import QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.form import PPanelBase

from .app import PQtWidget


panel_map = {
    PANEL_NONE: qt.QFrame.NoFrame | qt.QFrame.Plain,
    PANEL_BOX: qt.QFrame.Box | qt.QFrame.Plain,
    PANEL_RAISED: qt.QFrame.Panel | qt.QFrame.Raised,
    PANEL_SUNKEN: qt.QFrame.Panel | qt.QFrame.Sunken
}


def size_policy(align):
    horiz = vert = qt.QSizePolicy.MinimumExpanding
    if align in (ALIGN_LEFT, ALIGN_RIGHT):
        horiz = qt.QSizePolicy.Fixed
    elif align in (ALIGN_TOP, ALIGN_BOTTOM):
        vert = qt.QSizePolicy.Fixed
    return horiz, vert


class PPanel(PQtWidget, qt.QFrame, PPanelBase):
    
    def __init__(self, manager, parent, align=ALIGN_JUST, layout=LAYOUT_NONE, contents=None,
                 style=PANEL_NONE, margin=None, spacing=None):
        
        qt.QFrame.__init__(self, parent)
        self.setFrameStyle(panel_map[style])
        self.setSizePolicy(*size_policy(align))
        if layout == LAYOUT_HORIZONTAL:
            klass = qt.QHBoxLayout
        else:
            klass = qt.QVBoxLayout
        self._playout = klass()
        PPanelBase.__init__(self, manager, parent, align, layout, contents=contents,
                            style=style, margin=margin, spacing=spacing)
        # Qt 4/5 defaults don't seem to be the same as Qt 3, so compensate
        if margin is None:
            self.set_margin(0)
        if spacing is None:
            self.set_spacing(0)
    
    def set_box_width(self, width):
        self.setLineWidth(width)
    
    def set_margin(self, margin):
        self._playout.setContentsMargins(margin, margin, margin, margin)
    
    def set_spacing(self, spacing):
        self._playout.setSpacing(spacing)
    
    def add_widget(self, widget):
        self._playout.addWidget(widget)
    
    def do_layout(self):
        #self._playout.addStretch(1)
        self.setLayout(self._playout)
