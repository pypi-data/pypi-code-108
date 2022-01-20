#!/usr/bin/env python3
"""
Module TABLE -- UI Table Widgets
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.defs import *
from plib.ui.base import helpers

from .app import PWidgetBase


scrollbarsize = 20
gridlinesize = 2


class PTableRow(helpers._PRowHelperItem):
    """Table row helper class.
    
    Looks like a list of strings (the values in the cells
    in this row).
    """
    
    def _get_table(self):
        return self._helper
    
    def _get_row(self):
        return self._i
    
    table = property(_get_table)
    row = property(_get_row)
    
    def __len__(self):
        return self.table.colcount()
    
    def _get_data(self, index):
        return self.table._get_cell(self._i, index)
    
    def _set_data(self, index, value):
        self.table._set_cell(self._i, index, value)


class PTableLabelsBase(helpers._PHelperColLabels):
    """Table labels helper class.
    
    Note that the length of the list of labels passed to
    this class determines the column count of the table.
    """
    
    def _update(self, data):
        if self.table.colcount() != len(data):
            self.table.set_colcount(len(data))
        helpers._PHelperColLabels._update(self, data)
    
    def _get_table(self):
        return self._helper
    
    table = property(_get_table)


class PTableBase(PWidgetBase, helpers._PRowHelper):
    """Table class that looks like a list of PTableRows.
    
    Each PTableRow looks like a list of strings. Double-indexing
    the table by [row][col] therefore retrieves the string in
    cell row, col).
    """
    
    signals = (
        SIGNAL_CELLSELECTED,
        SIGNAL_CELLCHANGED,
    )
    
    item_class = PTableRow
    defaultcolwidth = 100
    defaultrowheight = 25
    defaultmargin = 25
    
    def __init__(self, manager, parent, labels=None, data=None,
                 font=None, header_font=None):
        
        PWidgetBase.__init__(self, manager, parent, font=font)
        helpers._PRowHelper.__init__(self, labels, data, header_font=header_font)
        
        # set minimum size after initializing data if there is data
        if data is not None:
            self.set_min_size(self.minwidth(), self.minheight())
    
    def _get_cell(self, row, col):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_cell(self, row, col, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def colcount(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_colcount(self, count):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_col(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_cell(self):
        item = self.current_item()
        c = self.current_col()
        if (not item) or (c < 0):
            return None
        else:
            return item[c]
    
    def topmargin(self):
        # Derived classes can override to return a better value
        return self.defaultmargin
    
    def leftmargin(self):
        # Derived classes can override to return a better value
        return self.defaultmargin
    
    def rowheight(self, row):
        return self.defaultrowheight
    
    def colwidth(self, col):
        return self.defaultcolwidth
    
    def minwidth(self):
        return (
            sum(self.colwidth(col) for col in range(self.colcount())) +
            self.leftmargin() + scrollbarsize +
            (self.colcount() * gridlinesize)
        )
    
    def minheight(self):
        return (
            sum(self.rowheight(row) for row in range(self.rowcount())) +
            self.topmargin() + scrollbarsize +
            (self.rowcount() * gridlinesize)
        )
    
    def force_repaint(self):
        """Placeholder for derived classes to implement.
        """
        pass
    
    def default_fgcolor(self):
        return COLOR_BLACK
    
    def default_bkcolor(self):
        return COLOR_WHITE
    
    def set_text_fgcolor(self, row, col, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_cell_bkcolor(self, row, col, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_row_fgcolor(self, row, color):
        for col in range(self.colcount()):
            self.set_text_fgcolor(row, col, color)
        self.force_repaint()
    
    def set_row_bkcolor(self, row, color):
        for col in range(self.colcount()):
            self.set_cell_bkcolor(row, col, color)
        self.force_repaint()
    
    def set_col_fgcolor(self, col, color):
        for row in range(self.rowcount()):
            self.set_text_fgcolor(row, col, color)
        self.force_repaint()
    
    def set_col_bkcolor(self, col, color):
        for row in range(self.rowcount()):
            self.set_cell_bkcolor(row, col, color)
        self.force_repaint()
