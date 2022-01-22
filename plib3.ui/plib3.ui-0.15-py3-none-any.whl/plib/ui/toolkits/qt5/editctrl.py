#!/usr/bin/env python3
"""
Module QT5.EDITCTRL -- Python Qt 5 Editing Widgets
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for edit controls.
"""

from PyQt5 import QtGui as qtg, QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.editctrl import PEditBoxBase, PNumEditBoxBase, PEditControlBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PQtEditBase(PQtWidgetBase):
    
    fn_get_read_only = 'isReadOnly'
    fn_set_read_only = 'setReadOnly'


class PQtEditBoxBase(qt.QLineEdit, PQtEditBase):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    fix_width_on_resize = True
    
    widget_class = qt.QLineEdit
    
    def __init__(self, parent):
        qt.QLineEdit.__init__(self, parent)
    
    def setup_expand(self, expand):
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
    
    def str_text(self):
        return str(self.text())
    
    def fix_width(self, width):
        # Qt line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)


class PEditBox(PQtEditBoxBase, PEditBoxBase,
               metaclass=PQtWidgetMeta):
    
    def __init__(self, manager, parent, text="",
                 geometry=None, expand=True):
        
        PQtEditBoxBase.__init__(self, parent)
        PEditBoxBase.__init__(self, manager, parent, text,
                              geometry=geometry, expand=expand)


class NumEditValidator(qtg.QIntValidator):
    
    def validate(self, input, pos):
        # For some reason Qt's int validator doesn't check this
        if len(str(input)) < 1:
            return qtg.QValidator.Invalid
        return super(NumEditValidator, self).validate(input, pos)


class PNumEditBox(PQtEditBoxBase, PNumEditBoxBase,
                  metaclass=PQtWidgetMeta):
    
    def __init__(self, manager, parent, value=0,
                 geometry=None, expand=True):
        
        PQtEditBoxBase.__init__(self, parent)
        PNumEditBoxBase.__init__(self, manager, parent, value,
                                 geometry=geometry, expand=expand)
        
        self.setValidator(NumEditValidator())


class PEditControl(qt.QPlainTextEdit, PQtEditBase, PEditControlBase,
                   metaclass=PQtWidgetMeta):
    
    fn_get_text = 'toPlainText'
    fn_set_text = 'setPlainText'
    
    fix_width_on_resize = True
    fix_height_on_resize = True
    
    widget_class = qt.QPlainTextEdit
    
    event_signals = (SIGNAL_TEXTSTATECHANGED,)
    
    def __init__(self, manager, parent, text="",
                 scrolling=False, font=None):
        
        # Flags for tracking state
        self._undoflag = False
        self._redoflag = False
        self._clipflag = False
        
        qt.QPlainTextEdit.__init__(self, parent)
        PEditControlBase.__init__(self, manager, parent, text,
                                  scrolling=scrolling, font=font)
        
        # Signal connections for tracking state
        statesigs = [
            ("undo", self._check_undoflag),
            ("redo", self._check_redoflag),
            ("copy", self._check_clipflag)
        ]
        for signame, target in statesigs:
            getattr(self, "{}Available".format(signame)).connect(target)
    
    def setup_scrolling(self, scrolling):
        if scrolling:
            self.setLineWrapMode(qt.QPlainTextEdit.NoWrap)
    
    fn_get_overwrite = 'overwriteMode'
    fn_set_overwrite = 'setOverwriteMode'
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # Qt text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
    
    def textStateChanged(self):
        self.do_notify(SIGNAL_TEXTSTATECHANGED)
    
    def _check_undoflag(self, available):
        self._undoflag = available
        self.textStateChanged()
    
    def _check_redoflag(self, available):
        self._redoflag = available
        self.textStateChanged()
    
    def _check_clipflag(self, available):
        self._clipflag = available
        self.textStateChanged()
    
    def can_undo(self):
        return self.isUndoRedoEnabled() and self._undoflag
    
    def can_redo(self):
        return self.isUndoRedoEnabled() and self._redoflag
    
    def can_clip(self):
        return self._clipflag
    
    def can_paste(self):
        return self.canPaste()
    
    def clear_edit(self):
        self.clear()
    
    def undo_last(self):
        self.undo()
    
    def redo_last(self):
        self.redo()
    
    def select_all(self):
        self.selectAll()
    
    def clear_selection(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
    
    def delete_last_cut(self):
        # Qt outputs an error message to the console, but this still
        # appears to work
        qt.QApplication.clipboard().clear()
    
    def copy_to_clipboard(self):
        self.copy()
    
    def cut_to_clipboard(self):
        self.cut()
    
    def paste_from_clipboard(self):
        self.paste()
