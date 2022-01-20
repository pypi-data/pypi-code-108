#!/usr/bin/env python3
"""
Module PYSIDE2.LABEL -- Python PySide 2 Text Label Widgets
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for text label widgets.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.label import PTextLabelBase

from .app import PQtWidget


class PTextLabel(PQtWidget, qt.QLabel, PTextLabelBase):
    
    fix_width_on_resize = True
    
    def __init__(self, manager, parent, text=None,
                 geometry=None, font=None):
        
        qt.QLabel.__init__(self, parent)
        PTextLabelBase.__init__(self, manager, parent, text,
                                geometry=geometry, font=font)
    
    fn_get_text = 'text'
    fn_set_text = 'setText'
