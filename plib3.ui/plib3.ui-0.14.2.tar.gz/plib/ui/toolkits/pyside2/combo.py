#!/usr/bin/env python3
"""
Module PYSIDE2.COMBO -- Python PySide 2 Combo Box Widgets
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for combo boxes.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.combo import PComboBoxBase, PNumComboBoxBase, PSortedComboBoxBase

from .app import PQtSequenceWidget


class PQtComboBoxBase(PQtSequenceWidget, qt.QComboBox):
    
    fix_width_on_resize = True
    
    def __init__(self, parent):
        qt.QComboBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)
    
    def current_text(self):
        return str(self.currentText())
    
    # Note that there's no quick override for set_current_text in Qt; the
    # corresponding method to the above doesn't do what we want (it changes
    # the stored text in the combo instead of selecting the text we give it)
    
    def current_index(self):
        return self.currentIndex()
    
    def set_current_index(self, index):
        self.setCurrentIndex(index)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return PComboBoxBase.count(self, value)
    
    def _indexlen(self):
        # Let this method access the Qt combo box count method.
        return qt.QComboBox.count(self)
    
    def _get_data(self, index):
        return str(self.itemText(index))
    
    def _set_data(self, index, value):
        self.setItemText(index, str(value))
    
    def _add_data(self, index, value):
        self.insertItem(index, str(value))
    
    def _del_data(self, index):
        self.removeItem(index)


class PComboBox(PQtComboBoxBase, PComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PQtComboBoxBase.__init__(self, parent)
        PComboBoxBase.__init__(self, manager, parent, items, value=value,
                               geometry=geometry)


class PNumComboBox(PQtComboBoxBase, PNumComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None):
        
        PQtComboBoxBase.__init__(self, parent)
        PNumComboBoxBase.__init__(self, manager, parent, items, value=value,
                                  geometry=geometry)


class PSortedComboBox(PQtComboBoxBase, PSortedComboBoxBase):
    
    def __init__(self, manager, parent, items=None, value=None,
                 geometry=None, key=None):
        
        PQtComboBoxBase.__init__(self, parent)
        PSortedComboBoxBase.__init__(self, manager, parent, items, value=value,
                                     geometry=geometry, key=key)
