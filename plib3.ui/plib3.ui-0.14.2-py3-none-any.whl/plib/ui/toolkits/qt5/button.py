#!/usr/bin/env python3
"""
Module QT5.BUTTON -- Python Qt 5 Button Widgets
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for button widgets.
"""

from PyQt5 import QtGui as qtg, QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.button import PButtonBase, PActionButtonBase, PCheckBoxBase

from .app import PQtWidgetMeta, PQtActionMixin, PQtWidgetBase


class PQtButtonBase(qt.QPushButton, PQtActionMixin, PQtWidgetBase):
    
    fix_width_on_resize = True
    
    widget_class = qt.QPushButton
    
    def __init__(self, parent,
                 geometry=None):
        
        qt.QPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
    
    def set_caption(self, caption):
        self.setText(caption)
    
    def set_icon_obj(self, icon):
        self.setIcon(icon)


class PButton(PQtButtonBase, PButtonBase,
              metaclass=PQtWidgetMeta):
    
    def __init__(self, manager, parent, caption, icon=None,
                 geometry=None):
        
        PQtButtonBase.__init__(self, parent)
        PButtonBase.__init__(self, manager, parent, caption, icon,
                             geometry=geometry)


class PActionButton(PQtButtonBase, PActionButtonBase,
                    metaclass=PQtWidgetMeta):
    
    event_signals = (SIGNAL_ACTIVATED,)
    
    def __init__(self, manager, parent, action,
                 geometry=None):
        
        PQtButtonBase.__init__(self, parent)
        PActionButtonBase.__init__(self, manager, parent, action,
                                   geometry=geometry)


class PCheckBox(qt.QCheckBox, PQtWidgetBase, PCheckBoxBase,
                metaclass=PQtWidgetMeta):
    
    fn_get_checked = 'isChecked'
    fn_set_checked = 'setChecked'
    
    widget_class = qt.QCheckBox
    
    def __init__(self, manager, parent, label, checked=None,
                 geometry=None, tristate=False):
        
        qt.QCheckBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        PCheckBoxBase.__init__(self, manager, parent, label, checked=checked,
                               geometry=geometry, tristate=tristate)
    
    def set_caption(self, caption):
        self.setText(caption)
    
    def make_tristate(self):
        self.setTriState(True)
