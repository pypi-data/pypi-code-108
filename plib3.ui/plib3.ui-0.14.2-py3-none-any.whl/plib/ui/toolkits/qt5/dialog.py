#!/usr/bin/env python3
"""
Module QT5.DIALOG -- Python Qt 5 Dialog Widget
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for the dialog widget.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.base.dialog import PDialogBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PDialog(qt.QDialog, PQtWidgetBase, PDialogBase,
              metaclass=PQtWidgetMeta):
    
    widget_class = qt.QDialog
    
    def __init__(self, manager, parent, caption, client=None,
                 accept_buttons=('ok', 'yes'), reject_buttons=('cancel', 'no')):
        
        qt.QDialog.__init__(self, parent)
        PDialogBase.__init__(self, manager, parent, caption, client,
                             accept_buttons=accept_buttons, reject_buttons=reject_buttons)
    
    def set_caption(self, caption):
        self.setWindowTitle(caption)
    
    def size_to_controls(self, width, height):
        self.resize(width, height)
    
    def display(self):
        self.show()
    
    def accept_changes(self):
        self.accept()
    
    def reject_changes(self):
        self.reject()
