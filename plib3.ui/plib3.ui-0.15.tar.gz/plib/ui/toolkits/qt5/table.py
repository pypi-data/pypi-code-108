#!/usr/bin/env python3
"""
Module QT5.TABLE -- Python Qt 5 Table Objects
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for the table widgets.
"""

import functools

from PyQt5 import QtGui as qtg, QtWidgets as qt

from plib.ui.defs import *
from plib.ui.base.table import PTableLabelsBase, PTableBase

from .app import PQtSequenceMeta, PQtWidgetBase, align_map
from .header import PQtHeaderBase, PQtHeaderWidget


class PTableLabels(PQtHeaderBase, PTableLabelsBase):
    
    def _set_labels_from_list(self, label_list):
        self.table.setHorizontalHeaderLabels(label_list)
    
    def _header_item(self, index):
        return self.table.horizontalHeaderItem()
    
    def _header_view(self):
        return self.table.horizontalHeader()

    def _set_align(self, index, align):
        self.table.horizontalHeaderItem(index).setTextAlignment(align_map[align])
        # Table cells will align themselves when added


class PTable(qt.QTableWidget, PQtHeaderWidget, PQtWidgetBase, PTableBase,
             metaclass=PQtSequenceMeta):
    
    widget_class = qt.QTableWidget
    
    labels_class = PTableLabels
    
    event_signals = (SIGNAL_CELLCHANGED,)
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        qt.QTableWidget.__init__(self, parent)
        self.setSortingEnabled(False)
        # Used by ugly hack in default fg and bk color methods, below
        pal = self.palette()
        self._def_fgcolor = pal.color(self.foregroundRole())
        self._def_bkcolor = pal.color(self.backgroundRole())
        # Used by ugly hack in setup_notify, below
        self._setting_colors = False
        
        # This will initialize data (if any)
        PTableBase.__init__(self, manager, parent, labels=labels, data=data,
                            font=font, header_font=header_font)
        
        # enable signals after initializing data so they don't get
        # fired on initialization
        self.setup_notify(SIGNAL_TABLECHANGED, self._tablechanged)
    
    def _tablechanged(self, row, col):
        # Filter out the signals we're not interested in
        if (row == self.current_row()) and (col == self.current_col()):
            self.do_notify(SIGNAL_CELLCHANGED, row, col)
    
    def wrap_target(self, signal, target):
        # Hack to mask out table changed events fired when cell colors are
        # changed (the Qt 4 API says this shouldn't happen but it does,
        # go figure)
        if signal == SIGNAL_TABLECHANGED:
            @functools.wraps(target)
            def _wrapper(row, col):
                if not self._setting_colors:
                    target(row, col)
            return _wrapper
        return target
    
    def _get_item(self, row, col):
        result = self.item(row, col)
        if not isinstance(result, qt.QTableWidgetItem):
            result = qt.QTableWidgetItem()
            self.setItem(row, col, result)
        return result
    
    def _get_cell(self, row, col):
        # Need str conversion here since widgets return QStrings
        return str(self._get_item(row, col).text())
    
    def _set_cell(self, row, col, value):
        item = self._get_item(row, col)  # this will fire table changed if row added
        item.setText(str(value))
        # FIXME: it would be nice if this could be done once instead of
        # per item
        item.setTextAlignment(self.horizontalHeaderItem(col).textAlignment())
    
    def header_object(self):
        return self.horizontalHeader()
    
    def rowcount(self):
        return self.rowCount()
    
    def colcount(self):
        return self.columnCount()
    
    def set_colcount(self, count):
        self.setColumnCount(count)
    
    def current_row(self):
        return self.currentRow()
    
    def current_col(self):
        return self.currentColumn()
    
    def _insert_row(self, index):
        self.insertRow(index)
    
    def _remove_row(self, index):
        self.removeRow(index)
    
    def topmargin(self):
        return 0  # self.topMargin()
    
    def leftmargin(self):
        return 0  # self.leftMargin()
    
    def rowheight(self, row):
        return self.rowHeight(row)
    
    def colwidth(self, col):
        return self.columnWidth(col)
    
    def default_fgcolor(self):
        return self._def_fgcolor
    
    def default_bkcolor(self):
        return self._def_bkcolor
    
    def set_text_fgcolor(self, row, col, color):
        item = self._get_item(row, col)
        self._setting_colors = True
        item.setForeground(qtg.QBrush(self._mapped_color(color)))
        self._setting_colors = False
    
    def set_cell_bkcolor(self, row, col, color):
        item = self._get_item(row, col)
        self._setting_colors = True
        item.setBackground(qtg.QBrush(self._mapped_color(color)))
        self._setting_colors = False
