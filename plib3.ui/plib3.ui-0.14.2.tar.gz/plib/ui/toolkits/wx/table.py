#!/usr/bin/env python3
"""
Module WX.TABLE -- Python wxWidgets Table Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets UI objects for table table.
"""

import functools

import wx.grid

from plib.ui.defs import *
from plib.ui.base.table import PTableLabelsBase, PTableBase, scrollbarsize, gridlinesize

from .app import PWxSequenceWidget, align_map


class PWxTableLabels(PTableLabelsBase):
    
    _contents = None
    _stretch = None
    
    def _set_label(self, index, label):
        self.table.SetColLabelValue(index, label)
    
    def _set_width(self, index, width):
        if width == WIDTH_STRETCH:
            # Can't compute stretch until all column widths are set
            if self._stretch is None:
                self._stretch = set()
            self._stretch.add(index)
        elif width == WIDTH_CONTENTS:
            # Can't compute sizing to contents until data is added
            if self._contents is None:
                self._contents = set()
            self._contents.add(index)
        elif width > 0:
            self.table.SetColSize(index, width)
    
    def _set_align(self, index, align):
        self.table.SetColLabelAlignment(align_map[align], wx.ALIGN_CENTER_VERTICAL)
    
    def _set_readonly(self, index, readonly):
        pass


class PTable(PWxSequenceWidget, wx.grid.Grid, PTableBase):
    
    labels_class = PWxTableLabels
    
    _align = True  # used by panel to determine placement
    _expand = True
    
    _initialized = False
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        wx.grid.Grid.__init__(self, parent)
        self.CreateGrid(0, 0)
        PTableBase.__init__(self, manager, parent, labels=labels, data=data,
                            font=font, header_font=header_font)
        
        self.SetColLabelSize(wx.grid.GRID_AUTOSIZE)
        self.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.SizeColumns()
        self._initialized = True  # so adding/deleting data now triggers SizeColumns
        
        # FIXME: We have to go through all this rigmarole because, first,
        # wx doesn't track the previous row/col in the cell selected event,
        # and second, wx fires the cell selected event before it updates the
        # widget methods that give the current row/col, so we have to roll
        # our own to allow event handlers to see the correct state, and third,
        # wx fires the cell selected event *before* the cell changed event if
        # you're editing a cell and then navigate to a new one
        self._editing_cell = False
        self._pending_select = None
        self.setup_notify(SIGNAL_TABLECELLSELECTED, self.OnCellSelected)
        self.setup_notify(SIGNAL_TABLECELLEDITING, self.OnCellEdit)
        self.setup_notify(SIGNAL_TABLECELLEDITDONE, self.OnCellEditDone)
        self.setup_notify(SIGNAL_TABLECHANGED, self.OnCellChanged)
        if self.labels._stretch:
            self.setup_notify(SIGNAL_SIZEEVENT, self.OnSizeEvent)
    
    def SizeColumns(self):
        # This handles the "fit to contents" columns; it has to be done first so the
        # stretch logic is using the correct values
        contents_indexes = self.labels._contents
        if not contents_indexes:
            return
        for col in contents_indexes:
            self.AutoSizeColumn(col, True)
        
        # This is factored out because it needs to be redone on size event
        self.StretchColumns()
    
    def _add(self, index, value):
        super(PTable, self)._add(index, value)
        if self._initialized:
            self.SizeColumns()
    
    def _del(self, index):
        super(PTable, self)._del(index, value)
        if self._initialized:
            self.SizeColumns()
    
    def OnCellSelected(self, event):
        new_row = event.GetRow()
        new_col = event.GetCol()
        if self._editing_cell:
            self._pending_select = (new_row, new_col)
        else:
            selected_fields = (
                ('CurrentRow', new_row),
                ('CurrentCol', new_col),
                ('PreviousRow', self.current_row()),
                ('PreviousCol', self.current_col()),
            )
            self.forward_event(SIGNAL_CELLSELECTED, event, selected_fields)
    
    def OnCellEdit(self, event):
        self._editing_cell = True
    
    # Temporary vars used by ugly hack in wrap_target below
    _row = None
    _col = None
    
    def OnCellEditDone(self, event):
        assert self._editing_cell
        self._row = event.GetRow()
        self._col = event.GetCol()
        changed_fields = (
            ('Row', self._row),
            ('Col', self._col),
        )
        self.forward_event(SIGNAL_CELLCHANGED, event, changed_fields)
    
    def wrap_target(self, signal, target):
        # Ugly hack so current_row and current_col return the correct values
        # inside the SIGNAL_CELLCHANGED handler, even if a new cell was
        # selected so the cell selected event fired first and updated the
        # wx grid's idea of what the current cell is
        target = super(PTable, self).wrap_target(signal, target)
        if signal == SIGNAL_CELLCHANGED:
            @functools.wraps(target)
            def _hack(*args, **kwargs):
                result = target(*args, **kwargs)
                self._row = None
                self._col = None
                return result
            return _hack
        return target
    
    def OnCellChanged(self, event):
        assert self._editing_cell
        self._editing_cell = False
        if self._pending_select:
            new_row, new_col = self._pending_select
            self._pending_select = None
            selected_fields = (
                ('CurrentRow', new_row),
                ('CurrentCol', new_col),
                # We cheat here by using the cell changed row/col as the previous row/col
                # for the cell select event (it would be really nice if wx would do this for us)
                ('PreviousRow', event.GetRow()),
                ('PreviousCol', event.GetCol()),
            )
            self.forward_event(SIGNAL_CELLSELECTED, event, selected_fields)
    
    def OnSizeEvent(self, event):
        self.StretchColumns()
    
    def StretchColumns(self):
        stretch_indexes = self.labels._stretch
        if not stretch_indexes:
            return
        for col in stretch_indexes:
            self.AutoSizeColumn(col, True)
        if self.get_width() > self.minwidth():
            stretch_count = len(stretch_indexes)
            base_width = sum(self.colwidth(col) for col in range(self.colcount()) if col not in stretch_indexes)
            border_width = self.leftmargin() + scrollbarsize + ((self.colcount() - stretch_count) * gridlinesize)
            stretch_width = (self.get_width() - base_width - border_width) // stretch_count
            for col in stretch_indexes:
                if stretch_width > self.colwidth(col):
                    self.labels._set_width(col, stretch_width)
    
    def set_header_font_object(self, font_name, font_size, bold, italic):
        self.SetLabelFont(self.wx_font_object(
            font_name, font_size, bold, italic
        ))
    
    def _get_cell(self, row, col):
        return self.GetCellValue(row, col)
    
    def _set_cell(self, row, col, value):
        self.SetCellValue(row, col, str(value))
    
    def rowcount(self):
        return self.GetNumberRows()
    
    def colcount(self):
        return self.GetNumberCols()
    
    def set_colcount(self, count):
        self.InsertCols(0, count)
    
    def current_row(self):
        # Must check above ugly hack for SIGNAL_CELLCHANGED first
        return self._row or self.GetGridCursorRow()
    
    def current_col(self):
        # Must check above ugly hack for SIGNAL_CELLCHANGED first
        return self._col or self.GetGridCursorCol()
    
    def _insert_row(self, index):
        self.InsertRows(index, 1)
    
    def _remove_row(self, index):
        self.DeleteRows(index, 1)
    
    def topmargin(self):
        return self.GetColLabelSize()
    
    def leftmargin(self):
        return self.GetRowLabelSize()
    
    def rowheight(self, row):
        return self.GetRowSize(row)
    
    def colwidth(self, col):
        return self.GetColSize(col)
    
    def force_repaint(self):
        self.Refresh()
    
    def default_fgcolor(self):
        return self.GetDefaultCellTextColour()
    
    def default_bkcolor(self):
        return self.GetDefaultCellBackgroundColour()
    
    def set_text_fgcolor(self, row, col, color):
        self.SetCellTextColour(row, col, self._mapped_color(color))
    
    def set_cell_bkcolor(self, row, col, color):
        self.SetCellBackgroundColour(row, col, self._mapped_color(color))
