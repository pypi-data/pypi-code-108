#!/usr/bin/env python3
"""
Module QT5.LABEL -- Python Qt 5 Text Label Widgets
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for text label widgets.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.base.label import PTextLabelBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PTextLabel(qt.QLabel, PQtWidgetBase, PTextLabelBase,
                 metaclass=PQtWidgetMeta):
    
    fix_width_on_resize = True
    
    widget_class = qt.QLabel
    
    def __init__(self, manager, parent, text=None,
                 geometry=None, font=None):
        
        qt.QLabel.__init__(self, parent)
        PTextLabelBase.__init__(self, manager, parent, text,
                                geometry=geometry, font=font)
    
    fn_get_text = 'text'
    fn_set_text = 'setText'
