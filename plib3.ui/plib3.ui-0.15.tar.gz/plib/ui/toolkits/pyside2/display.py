#!/usr/bin/env python3
"""
Module PYSIDE2.DISPLAY -- Python PySide 2 Text Display Widgets
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI objects for text display widgets.
"""

from PySide2 import QtWidgets as qt

from plib.ui.base.display import PTextDisplayBase

from .app import PQtWidget


class PTextDisplay(PQtWidget, qt.QPlainTextEdit, PTextDisplayBase):
    
    fix_width_on_resize = True
    fix_height_on_resize = True
    
    def __init__(self, manager, parent, text=None,
                 scrolling=False, font=None):
        
        qt.QPlainTextEdit.__init__(self, parent)
        self.setReadOnly(True)
        PTextDisplayBase.__init__(self, manager, parent, text,
                                  scrolling=scrolling, font=font)
    
    def setup_scrolling(self, scrolling):
        if scrolling:
            self.setLineWrapMode(qt.QPlainTextEdit.NoWrap)
    
    def get_text(self):
        return self.toPlainText()
    
    def set_text(self, value):
        self.setPlainText(value)
    
    def add_text(self, value):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(value)
    
    def clear_text(self):
        self.clear()
