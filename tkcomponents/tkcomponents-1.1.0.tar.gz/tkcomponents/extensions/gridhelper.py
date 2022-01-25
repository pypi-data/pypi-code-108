from objectextensions import Extension

from typing import Iterable

from ..component import Component


class GridHelper(Extension):
    @staticmethod
    def extend(target_cls):
        Extension._set(target_cls, "_apply_frame_stretch", GridHelper.__apply_frame_stretch)
        Extension._set(target_cls, "_apply_dividers", GridHelper.__apply_dividers)

    @staticmethod
    def can_extend(target_cls):
        return issubclass(target_cls, Component)

    def __apply_frame_stretch(self, rows: Iterable[int] = (), columns: Iterable[int] = (), weight: int = 1) -> None:
        """
        Sets the specified rows and columns to be able to expand as needed when the component expands to fit
        its container. The weight parameter dictates in what ratio the rows and columns expand relative
        to each other
        """

        for row_index in rows:
            self._frame.grid_rowconfigure(row_index, weight=weight)
        for column_index in columns:
            self._frame.grid_columnconfigure(column_index, weight=weight)

    def __apply_dividers(self, divider_size: int, rows: Iterable[int] = (), columns: Iterable[int] = ()) -> None:
        """
        Sets the specified rows and columns to have a minimum size, so that they will always separate the surrounding
        rows and columns
        """

        for row_index in rows:
            self._frame.grid_rowconfigure(row_index, minsize=divider_size)
        for column_index in columns:
            self._frame.grid_columnconfigure(column_index, minsize=divider_size)
