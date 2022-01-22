#!/usr/bin/env python3
"""
Module QT5.DISPLAY -- Python Qt 5 Text Display Widgets
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for text display widgets.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.base.display import PTextDisplayBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PTextDisplay(qt.QPlainTextEdit, PQtWidgetBase, PTextDisplayBase,
                   metaclass=PQtWidgetMeta):
    
    fix_width_on_resize = True
    fix_height_on_resize = True
    
    widget_class = qt.QPlainTextEdit
    
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
