#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Utility functions for images."""
import typing as t
from enum import Enum
from functools import lru_cache
from pathlib import Path

import numpy as np
from typing_extensions import Literal

from pyxel.inputs import load_image


class Alignment(Enum):
    """Alignment class."""

    center = "center"
    top_left = "top_left"
    top_right = "top_right"
    bottom_left = "bottom_left"
    bottom_right = "bottom_right"


def _set_relative_position(
    array_x: int,
    array_y: int,
    output_x: int,
    output_y: int,
    alignment: Alignment,
) -> t.Tuple[int, int]:
    """Calculate relative position of (0, 0) pixels for two different array shapes based on desired alignment.

    Parameters
    ----------
    output_y: int
    output_x: int
    array_y: int
    array_x: int
    alignment: Alignment

    Returns
    -------
    tuple
    """
    if alignment == Alignment.center:
        return int((output_y - array_y) / 2), int((output_x - array_x) / 2)
    elif alignment == Alignment.top_left:
        return 0, 0
    elif alignment == Alignment.top_right:
        return 0, output_x - array_x
    elif alignment == Alignment.bottom_left:
        return output_y - array_y, 0
    elif alignment == Alignment.bottom_right:
        return output_y - array_y, output_x - array_x
    else:
        raise NotImplementedError


def fit_into_array(
    array: np.ndarray,
    output_shape: t.Tuple[int, ...],
    relative_position: t.Tuple[int, int] = (0, 0),
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
    allow_smaller_array: bool = True,
) -> np.ndarray:
    """Fit input array into an output array of specified output shape.

    Input array can be either larger or smaller than output array. In the first case the input array will be cropped.
    The relative position between the arrays in the coordinate system is specified with argument relative_position.
    It is a tuple with coordinates (Y,X).
    User can use this argument to specify the position of input array values in the output array.
    If arrays are to be aligned in the center or one of the corners,
    it is also possible with argument align and passing a location keyword.
    User can turn on that smaller arrays than output shape are not allowed by setting allow_smaller_array to False.

    Parameters
    ----------
    array: ndarray
    output_shape: tuple
    relative_position: tuple
    align: {'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right'}, default: None
    allow_smaller_array: bool

    Returns
    -------
    output: ndarray
    """

    array_y, array_x = array.shape
    output = np.zeros(output_shape)
    output_y, output_x = output_shape

    if not allow_smaller_array:
        if array_y < output_y or array_x < output_y:
            raise ValueError("Input array too small to fit into the desired shape!.")

    if align:
        relative_position = _set_relative_position(
            array_x=array_x,
            array_y=array_y,
            output_x=output_x,
            output_y=output_y,
            alignment=Alignment(align),
        )

    array_y_coordinates = np.array(
        range(relative_position[0], relative_position[0] + array_y)
    )
    array_x_coordinates = np.array(
        range(relative_position[1], relative_position[1] + array_x)
    )
    output_y_coordinates = np.array(range(output_y))
    output_x_coordinates = np.array(range(output_x))

    overlap_y = np.intersect1d(array_y_coordinates, output_y_coordinates)
    overlap_x = np.intersect1d(array_x_coordinates, output_x_coordinates)

    if overlap_y.size == 0 and overlap_x.size == 0:
        raise ValueError("No overlap of array and target in Y and X dimension.")
    elif overlap_y.size == 0:
        raise ValueError("No overlap of array and target in Y dimension.")
    elif overlap_x.size == 0:
        raise ValueError("No overlap of array and target in X dimension.")

    cropped_array = array[
        slice(
            overlap_y[0] - relative_position[0],
            overlap_y[-1] + 1 - relative_position[0],
        ),
        slice(
            overlap_x[0] - relative_position[1],
            overlap_x[-1] + 1 - relative_position[1],
        ),
    ]

    output[
        slice(overlap_y[0], overlap_y[-1] + 1), slice(overlap_x[0], overlap_x[-1] + 1)
    ] = cropped_array

    return output


@lru_cache(maxsize=128)  # One must add parameter 'maxsize' for Python 3.7
def load_cropped_and_aligned_image(
    shape: t.Tuple[int, ...],
    filename: t.Union[str, Path],
    position_x: int = 0,
    position_y: int = 0,
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
    allow_smaller_array: bool = True,
) -> np.ndarray:
    """Load image from file and fit to detector shape.

    Parameters
    ----------
    shape: tuple
        Detector shape.
    filename: str
        Path to image file.
    position_x: tuple
        Index of starting column, used when fitting image to detector.
    position_y: tuple
        Index of starting row, used when fitting image to detector.
    align: Literal
        Keyword to align the image to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")

    Returns
    -------
    cropped_and_aligned_image: ndarray
    """
    # Load 2d image (which can be smaller or
    #                         larger in dimensions than detector imaging area)
    image = load_image(filename)

    cropped_and_aligned_image = fit_into_array(
        array=image,
        output_shape=shape,
        relative_position=(position_y, position_x),
        align=align,
        allow_smaller_array=allow_smaller_array,
    )  # type: np.ndarray

    return cropped_and_aligned_image
