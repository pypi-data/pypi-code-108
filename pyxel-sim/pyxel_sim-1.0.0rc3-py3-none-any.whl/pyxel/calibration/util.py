#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import typing as t
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd

from pyxel import load_datacube, load_image

if t.TYPE_CHECKING:
    import xarray as xr

#  from pyxel.pipelines import Processor
__all__ = [
    "CalibrationResult",
    "CalibrationMode",
    "Island",
    "check_ranges",
    "list_to_slice",
    "read_data",
]


class CalibrationResult(t.NamedTuple):
    """Result class for calibration class."""

    dataset: "xr.Dataset"
    processors: pd.DataFrame
    logs: pd.DataFrame
    filenames: t.Sequence


class CalibrationMode(Enum):
    """TBW."""

    Pipeline = "pipeline"
    SingleModel = "single_model"


class Island(Enum):
    """User defines num_islands provides by Pygmo."""

    MultiProcessing = "multiprocessing"
    MultiThreading = "multithreading"
    IPyParallel = "ipyparallel"


def read_single_data(filename: Path) -> np.ndarray:
    """Read a numpy array from a FITS or NPY file.

    Parameters
    ----------
    filename : Path

    Returns
    -------
    array
        TBW.
    """
    # Late import to avoid circular import

    data = load_image(filename)

    # # TODO: Is it the right manner ?
    # if data is None:
    #     raise OSError(f"Input file '{filename}' can not be read by Pyxel.")

    return data


def read_single_datacube(filename: Path) -> np.ndarray:
    """Read a numpy array from a FITS or NPY file.

    Parameters
    ----------
    filename : Path

    Returns
    -------
    array
        TBW.
    """

    data = load_datacube(filename)

    # # TODO: Is it the right manner ?
    # if data is None:
    #     raise OSError(f"Input file '{filename}' can not be read by Pyxel.")

    return data


def read_datacubes(filenames: t.Sequence[Path]) -> t.Sequence[np.ndarray]:
    """Read numpy array(s) from several FITS or NPY files.

    :param filenames:
    :return:
    """
    output = [
        read_single_datacube(Path(filename)) for filename in filenames
    ]  # type: t.Sequence[np.ndarray]

    return output


def read_data(filenames: t.Sequence[Path]) -> t.Sequence[np.ndarray]:
    """Read numpy array(s) from several FITS or NPY files.

    :param filenames:
    :return:
    """
    output = [
        read_single_data(Path(filename)) for filename in filenames
    ]  # type: t.Sequence[np.ndarray]

    return output


# TODO: Refactor and add more unit tests. See #327
def list_to_slice(
    input_list: t.Optional[t.Sequence[int]] = None,
) -> t.Union[t.Tuple[slice, slice], t.Tuple[slice, slice, slice]]:
    """TBW.

    :return:
    """
    if not input_list:
        return slice(None), slice(None)

    elif len(input_list) == 4:
        return slice(input_list[0], input_list[1]), slice(input_list[2], input_list[3])

    elif len(input_list) == 6:
        return (
            slice(input_list[0], input_list[1]),
            slice(input_list[2], input_list[3]),
            slice(input_list[4], input_list[5]),
        )

    else:
        raise ValueError("Fitting range should have 4 or 6 values")


# TODO: Refactor and add more unit tests. See #327
def list_to_3d_slice(
    input_list: t.Optional[t.Sequence[int]] = None,
) -> t.Tuple[slice, slice, slice]:
    """TBW.

    :return:
    """
    if not input_list:
        return slice(None), slice(None), slice(None)

    elif len(input_list) == 6:
        return (
            slice(input_list[0], input_list[1]),
            slice(input_list[2], input_list[3]),
            slice(input_list[4], input_list[5]),
        )

    else:
        raise ValueError("Fitting range should have 6 values")


def slice_to_range(data: slice) -> range:
    """Convert a slice to a range.

    Examples
    --------
    >>> slice_to_range(slice(10))
    range(10)
    >>> slice_to_range(slice(10, 20))
    range(10, 20)
    >>> slice_to_range(slice(10, 20, 2))
    ValueError("Cannot use parameter 'step' in the slice object.")

    Raises
    ------
    ValueError
        If the input slice is not correct.
    """
    if data.step is not None:
        raise ValueError("Cannot use parameter 'step' in the slice object.")
    if data.stop is None:
        raise ValueError("Missing 'stop' parameter in the slice object")

    if data.start is None:
        result = range(data.stop)

        if data.stop <= 0:
            raise ValueError("Parameter 'stop' must be strictly greater than 'start'")
    else:
        if data.start < 0:
            raise ValueError("Parameter 'start' must be strictly positive")
        if data.start >= data.stop:
            raise ValueError("Parameter 'stop' must be strictly greater than 'start'")

        result = range(data.start, data.stop)

    return result


# TODO: Refactor and add more unit tests. See #328
def check_ranges(
    target_fit_range: t.Sequence[int],
    out_fit_range: t.Sequence[int],
    rows: int,
    cols: int,
    readout_times: t.Optional[int] = None,
) -> None:
    """TBW."""
    if target_fit_range:
        if len(target_fit_range) not in (4, 6):
            raise ValueError

        if out_fit_range:
            if len(out_fit_range) not in (4, 6):
                raise ValueError

            if (target_fit_range[1] - target_fit_range[0]) != (
                out_fit_range[1] - out_fit_range[0]
            ):
                raise ValueError(
                    "Fitting ranges have different lengths in 1st dimension"
                )

            # TODO: Refactor and add more unit tests. See #328
            if len(target_fit_range) == 4 and len(out_fit_range) == 4:
                if (target_fit_range[3] - target_fit_range[2]) != (
                    out_fit_range[3] - out_fit_range[2]
                ):
                    raise ValueError(
                        "Fitting ranges have different lengths in 2nd dimension"
                    )

            if len(target_fit_range) == 6 and len(out_fit_range) == 6:
                if (target_fit_range[5] - target_fit_range[4]) != (
                    out_fit_range[5] - out_fit_range[4]
                ):
                    raise ValueError(
                        "Fitting ranges have different lengths in third dimension"
                    )

        # for i in [0, 1]:
        #     # TODO: Refactor and add more unit tests. See #328
        #     if not (0 <= target_fit_range[i] <= rows):
        #         raise ValueError("Value of target fit range is wrong")

        for i in [-3, -4]:
            if not (0 <= target_fit_range[i] <= rows):
                raise ValueError("Value of target fit range is wrong")

        for i in [-1, -2]:
            if not (0 <= target_fit_range[i] <= cols):
                raise ValueError("Value of target fit range is wrong")

        if len(target_fit_range) == 6:
            if readout_times is None:
                raise ValueError("Target data is not a 3 dimensional array")

            for i in [0, 1]:
                # TODO: Refactor and add more unit tests. See #328
                if not (0 <= target_fit_range[i] <= readout_times):
                    raise ValueError("Value of target fit range is wrong")
