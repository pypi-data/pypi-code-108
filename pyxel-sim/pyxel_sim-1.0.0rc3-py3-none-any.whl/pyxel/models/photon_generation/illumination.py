#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models."""
import typing as t

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector


def rectangular(
    shape: t.Tuple[int, int],
    level: float,
    object_size: t.Optional[t.Sequence[int]] = None,
    object_center: t.Optional[t.Sequence[int]] = None,
) -> np.ndarray:
    """Calculate an image of a rectangular object.

    Parameters
    ----------
    shape: tuple
        Shape of the output array.
    level: float
        Flux of photon per pixel.
    object_size: list or tuple, optional
        List or tuple of length 2, integers defining the diameters of the rectangular object
        in vertical and horizontal directions.
    object_center: list or tuple, optional
        List or tuple of length 2, two integers (row and column number),
        defining the coordinates of the center of the rectangular object.

    Returns
    -------
    photon_array: ndarray
        Output numpy array.
    """
    if not object_size:
        raise ValueError(
            "object_size argument should be defined for illumination model"
        )
    if object_size and not len(object_size) == 2:
        raise ValueError("Object size should be a sequence of length 2!")
    if object_center and not len(object_center) == 2:
        raise ValueError("Object size should be a sequence of length 2!")

    photon_array = np.zeros(shape, dtype=float)
    if object_center is not None:
        if not (
            (0 <= object_center[0] <= shape[0]) and (0 <= object_center[1] <= shape[1])
        ):
            raise ValueError('Argument "object_center" should be inside Photon array.')
    else:
        object_center = [int(shape[0] / 2), int(shape[1] / 2)]
    p = object_center[0] - int(object_size[0] / 2)
    q = object_center[1] - int(object_size[1] / 2)
    p0 = int(np.clip(p, a_min=0, a_max=shape[0]))
    q0 = int(np.clip(q, a_min=0, a_max=shape[1]))
    photon_array[slice(p0, p + object_size[0]), slice(q0, q + object_size[1])] = level

    return photon_array


def elliptic(
    shape: t.Tuple[int, int],
    level: float,
    object_size: t.Optional[t.Sequence[int]] = None,
    object_center: t.Optional[t.Sequence[int]] = None,
) -> np.ndarray:
    """Calculate an image of an elliptic object.

    Parameters
    ----------
    shape: tuple
        Shape of the output array.
    level: float
        Flux of photon per pixel.
    object_size: list or tuple, optional
        List or tuple of length 2, integers defining the diameters of the elliptic object
        in vertical and horizontal directions.
    object_center: list or tuple, optional
        List or tuple of length 2, two integers (row and column number),
        defining the coordinates of the center of the elliptic object.

    Returns
    -------
    photon_array: ndarray
        Output numpy array.
    """
    if not object_size:
        raise ValueError(
            "object_size argument should be defined for illumination model"
        )
    if object_size and not len(object_size) == 2:
        raise ValueError("Object size should be a sequence of length 2!")
    if object_center and not len(object_center) == 2:
        raise ValueError("Object size should be a sequence of length 2!")

    photon_array = np.zeros(shape, dtype=float)
    if object_center is not None:
        if not (
            (0 <= object_center[0] <= shape[0]) and (0 <= object_center[1] <= shape[1])
        ):
            raise ValueError('Argument "object_center" should be inside Photon array.')
    else:
        object_center = [int(shape[0] / 2), int(shape[1] / 2)]
    y, x = np.ogrid[: shape[0], : shape[1]]
    dist_from_center = np.sqrt(
        ((x - object_center[1]) / float(object_size[1] / 2)) ** 2
        + ((y - object_center[0]) / float(object_size[0] / 2)) ** 2
    )
    photon_array[dist_from_center < 1] = level
    return photon_array


def calculate_illumination(
    shape: t.Tuple[int, int],
    level: float,
    option: str = "uniform",
    object_size: t.Optional[t.Sequence[int]] = None,
    object_center: t.Optional[t.Sequence[int]] = None,
) -> np.ndarray:
    """Calculate the array of photons uniformly over the entire array or over a object.

    Parameters
    ----------
    shape: tuple
        Shape of the output array.
    level: float
        Flux of photon per pixel.
    option: str{'uniform', 'elliptic_hole', 'rectangular_hole'}
        A string indicating the type of illumination:
        - ``uniform``
           Uniformly fill the entire array with photon. (Default)
        - ``elliptic_hole``
           Mask with elliptic object.
        - ``rectangular_hole``
           Mask with rectangular object.
    object_size: list or tuple, optional
        List or tuple of length 2, integers defining the diameters of the elliptic or rectangular object
        in vertical and horizontal directions.
    object_center: list or tuple, optional
        List or tuple of length 2, two integers (row and column number),
        defining the coordinates of the center of the elliptic or rectangular object.

    Returns
    -------
    photon_array: ndarray
        Output numpy array.
    """
    if option == "uniform":
        photon_array = np.ones(shape, dtype=float) * level
    elif option == "rectangular":
        photon_array = rectangular(
            shape=shape,
            object_size=object_size,
            object_center=object_center,
            level=level,
        )
    elif option == "elliptic":
        photon_array = elliptic(
            shape=shape,
            object_size=object_size,
            object_center=object_center,
            level=level,
        )
    else:
        raise NotImplementedError

    return photon_array


def illumination(
    detector: Detector,
    level: float,
    option: Literal["uniform", "rectangular_hole", "elliptic_hole"] = "uniform",
    object_size: t.Optional[t.Sequence[int]] = None,
    object_center: t.Optional[t.Sequence[int]] = None,
    time_scale: float = 1.0,
) -> None:
    """Generate photon uniformly over the entire array or over an elliptic or rectangular object.

    detector: Detector
        Pyxel Detector object.
    level: float
        Flux of photon per pixel.
    option: str
        A string indicating the type of illumination:
        - ``uniform``
        Uniformly fill the entire array with photon. (Default)
        - ``elliptic``
        Mask with elliptic object.
        - ``rectangular``
        Mask with rectangular object.
    object_size: list or tuple, optional
        List or tuple of length 2, integers defining the diameters of the elliptic or rectangular object
        in vertical and horizontal directions.
    object_center: list or tuple, optional
        List or tuple of length 2, two integers (row and column number),
        defining the coordinates of the center of the elliptic or rectangular object.
    time_scale: float
        Time scale of the photon flux, default is 1 second. 0.001 would be ms.
    """
    shape = (detector.geometry.row, detector.geometry.col)

    photon_array = calculate_illumination(
        shape=shape,
        level=level,
        option=option,
        object_size=object_size,
        object_center=object_center,
    )

    photon_array = photon_array * (detector.time_step / time_scale)

    try:
        detector.photon.array += photon_array
    except ValueError as ex:
        raise ValueError("Shapes of arrays do not match") from ex
