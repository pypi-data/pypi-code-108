#!/usr/bin/env python3
"""
Module PYSIDE2.DIALOG -- Python PySide 2 Dialog Widget
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for the dialog widget.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.dialog import PDialogBase

from .app import PQtWidget


class PDialog(PQtWidget, qt.QDialog, PDialogBase):
    
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
