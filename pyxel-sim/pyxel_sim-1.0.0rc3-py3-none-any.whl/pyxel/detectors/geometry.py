#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Geometry class for detector."""
import numpy as np

from pyxel.util.memory import get_size
import typing as t


def get_vertical_pixel_center_pos(
    num_rows: int,
    num_cols: int,
    pixel_vertical_size: float,
) -> np.ndarray:
    """Generate vertical position list of all pixel centers in detector imaging area."""
    init_ver_position = np.arange(0.0, num_rows, 1.0) * pixel_vertical_size
    init_ver_position += pixel_vertical_size / 2.0

    return np.repeat(init_ver_position, num_cols)


def get_horizontal_pixel_center_pos(
    num_rows: int,
    num_cols: int,
    pixel_horizontal_size: float,
) -> np.ndarray:
    """Generate horizontal position list of all pixel centers in detector imaging area."""
    init_hor_position = np.arange(0.0, num_cols, 1.0) * pixel_horizontal_size
    init_hor_position += pixel_horizontal_size / 2.0

    return np.tile(init_hor_position, reps=num_rows)


class Geometry:
    """Geometrical attributes of the detector.

    Parameters
    ----------
    row: int
        Number of pixel rows.
    col: int
        Number of pixel columns.
    total_thickness: float, optional
        Thickness of detector. Unit: um
    pixel_vert_size: float, optional
        Vertical dimension of pixel. Unit: um
    pixel_horz_size: float, optional
        Horizontal dimension of pixel. Unit: um
    """

    def __init__(
        self,
        row: int,
        col: int,
        total_thickness: t.Optional[float] = None,  # unit: um
        pixel_vert_size: t.Optional[float] = None,  # unit: um
        pixel_horz_size: t.Optional[float] = None,  # unit: um
    ):
        if row not in range(10001):
            raise ValueError("'row' must be between 0 and 10000.")

        if col not in range(10001):
            raise ValueError("'col' must be between 0 and 10000.")

        if total_thickness and not (0.0 <= total_thickness <= 10000.0):
            raise ValueError("'total_thickness' must be between 0.0 and 10000.0.")

        if pixel_vert_size and not (0.0 <= pixel_vert_size <= 1000.0):
            raise ValueError("'pixel_vert_size' must be between 0.0 and 1000.0.")

        if pixel_horz_size and not (0.0 <= pixel_horz_size <= 1000.0):
            raise ValueError("'pixel_horz_size' must be between 0.0 and 1000.0.")

        self._row = row
        self._col = col
        self._total_thickness = total_thickness
        self._pixel_vert_size = pixel_vert_size
        self._pixel_horz_size = pixel_horz_size

        self._numbytes = 0

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return (
            f"{cls_name}(row={self._row!r}, col={self._col!r}, "
            f"total_thickness={self._total_thickness!r}, "
            f"pixel_vert_size={self._pixel_vert_size!r}, "
            f"pixel_horz_size={self._pixel_horz_size})"
        )

    @property
    def row(self) -> int:
        """Get Number of pixel rows."""
        return self._row

    @row.setter
    def row(self, value: int) -> None:
        """Set Number of pixel rows."""
        if value not in range(10001):
            raise ValueError("'row' must be between 0 and 10000.")

        self._row = value

    @property
    def col(self) -> int:
        """Get Number of pixel columns."""
        return self._col

    @col.setter
    def col(self, value: int) -> None:
        """Set Number of pixel columns."""
        if value not in range(10001):
            raise ValueError("'columns' must be between 0 and 10000.")

        self._col = value

    @property
    def total_thickness(self) -> float:
        """Get Thickness of detector."""
        if self._total_thickness:
            return self._total_thickness
        else:
            raise ValueError("'total_thickness' not specified in detector geometry.")

    @total_thickness.setter
    def total_thickness(self, value: float) -> None:
        """Set Thickness of detector."""
        if not (0.0 <= value <= 10000.0):
            raise ValueError("'total_thickness' must be between 0.0 and 10000.0.")

        self._total_thickness = value

    @property
    def pixel_vert_size(self) -> float:
        """Get Vertical dimension of pixel."""
        if self._pixel_vert_size:
            return self._pixel_vert_size
        else:
            raise ValueError("'pixel_vert_size' not specified in detector geometry.")

    @pixel_vert_size.setter
    def pixel_vert_size(self, value: float) -> None:
        """Set Vertical dimension of pixel."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'pixel_vert_size' must be between 0.0 and 1000.0.")

        self._pixel_vert_size = value

    @property
    def pixel_horz_size(self) -> float:
        """Get Horizontal dimension of pixel."""
        if self._pixel_horz_size:
            return self._pixel_horz_size
        else:
            raise ValueError("'pixel_horz_size' not specified in detector geometry.")

    @pixel_horz_size.setter
    def pixel_horz_size(self, value: float) -> None:
        """Set Horizontal dimension of pixel."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'pixel_horz_size' must be between 0.0 and 1000.0.")

        self._pixel_horz_size = value

    @property
    def horz_dimension(self) -> float:
        """Get total horizontal dimension of detector. Calculated automatically.

        Return
        ------
        float
            horizontal dimension
        """
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self) -> float:
        """Get total vertical dimension of detector. Calculated automatically.

        Return
        ------
        float
            vertical dimension
        """
        return self.pixel_vert_size * self.row

    def vertical_pixel_center_pos_list(self) -> np.ndarray:
        """Generate horizontal position list of all pixel centers in detector imaging area."""
        return get_vertical_pixel_center_pos(
            num_rows=self.row,
            num_cols=self.col,
            pixel_vertical_size=self.pixel_vert_size,
        )

    def horizontal_pixel_center_pos_list(self) -> np.ndarray:
        """Generate horizontal position list of all pixel centers in detector imaging area."""
        return get_horizontal_pixel_center_pos(
            num_rows=self.row,
            num_cols=self.col,
            pixel_horizontal_size=self.pixel_horz_size,
        )

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes
