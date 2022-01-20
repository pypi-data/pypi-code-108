# coding=utf-8
"""
(C) FHCS GmbH

Iterator class, instantiated object returns (row, column) tuples to walk through tables starting from top left
corner down to the bottom right corner, to iterate through the table cells, for each next diagonal cell it returns
cells to the left of it ant to the top of it sequentally.

To use for MS Excel tables parsing, specifically for looking the main key tag of the import onm the sheet.
"""

from typing import Tuple


class DiagonalTableWalk:
    """
    Iterator class, instantiated object returns (row, column) tuples to walk through tables starting from top left
    corner down to the bottom right corner, to iterate through the table cells, for each next diagonal cell it returns
    cells to the left of it ant to the top of it sequentally. The algorithm does not search through entire table in
    case if table is not square - in this case the small tail of the table is skipped for sake of simplicity.
    Skipped tail size is not more than half of the remainder of division of bigger dimension by smaller dimension,
    like if table has 55 rows and 10 columns, then 25 (5x5) cells in the bottom right part of table will be skipped.
    """
    def __init__(self, maxrow: int, maxcol: int):
        """
        Pass limit values of the table to iterate through

        :param maxrow: the last table row to iterate through
        :param maxcol: the last table column to iterate through
        """
        self._maxrow = maxrow
        self._maxcol = maxcol
        # True if the table is non square and vertical, False if horizontal, None if table is square
        self._shape = None
        if self._maxrow > self._maxcol:
            self._shape = True
        elif self._maxrow < self._maxcol:
            self._shape = False
        # Shifts for non square tables - always start from top left, so 0 at the class instantiation
        self._rowshift = 0
        self._colshift = 0
        # Current row, start from top left
        self._row = None
        # Current column, start from top left
        self._col = None
        # Current diagonal bottom right corner, start from top left
        self._diag = 1
        # Current step from diagonal, start from 0, means first return the diagonal element itself,
        # it counts up to self._diag
        self._step = 0
        # Output trigger, True means return upper cursor, False means return left cursor, start with True
        self._cursor_switch = True

    def __next__(self) -> Tuple[int, int]:
        """
        Cacluates and returns the next tuple
        """
        # Updates the position of the cursor depending on the current self._diag,
        # self._step and self._cursor_switch values
        self._update()
        # And return the positioned cursor values
        return self._row, self._col

    def __iter__(self):
        """
        Returns self
        """
        return self

    def _update(self):
        """
        Positions the cursor depending on the switch
        """
        if self._step == 0:
            # If we are on the diagonal, position cursor on diagonal, this happens only on the first iteration
            self._row = self._rowshift + self._diag
            self._col = self._colshift + self._diag
            # and increment the step, because we have to increment distance of cursor from diagonal
            self._step += 1
        elif 0 < self._step < self._diag:
            # If we are not on the diagonal, but still inside the table
            if self._cursor_switch:
                # If self._cursor_switch is True, position cursor on the upper location,
                # at self._step distance from diagonal
                self._row = self._rowshift + self._diag - self._step
                self._col = self._colshift + self._diag
                # switch to False
                self._cursor_switch = False
            else:
                # If self._cursor_switch is False, position cursor on the left location,
                # at self._step distance from diagonal
                self._row = self._rowshift + self._diag
                self._col = self._colshift + self._diag - self._step
                # switch to True
                self._cursor_switch = True
                # and increment the step, because we have to increment distance of cursor from diagonal
                self._step += 1
        elif self._step == self._diag:
            # If we are not on the diagonal, and ran out of table,
            # increment the diagonal and set self._cursor_switch to True
            if self._check():
                self._diag += 1
                self._cursor_switch = True
                # And we are again on the diagonal, position cursor on diagonal
                self._row = self._rowshift + self._diag
                self._col = self._colshift + self._diag
                # Always drop the tail search
                if self._row > self._maxrow or self._col > self._maxcol:
                    raise StopIteration
                # drop the self._step to 1, for the next iteration
                self._step = 1
            else:
                raise StopIteration

    def _check(self) -> bool:
        """
        Checks max rows and columns to handle non square tables, and shifts the origin when needed
        """
        if self._shape is None:
            # Square table, just check limits for self._diag
            if self._diag < self._maxrow:
                return True
            else:
                return False
        else:
            # Table is not square
            if self._shape:
                # Table is vertical rows > columns
                if self._diag == self._maxcol:
                    # Shift row origin
                    self._rowshift += self._maxcol
                    # Reset self._diag to 0
                    self._diag = 0
            else:
                # Table is horizontal columns > rows
                if self._diag == self._maxrow:
                    # Shift column origin
                    self._colshift += self._maxrow
                    # Reset self._diag to 0
                    self._diag = 0
            # By default return True
            return True
