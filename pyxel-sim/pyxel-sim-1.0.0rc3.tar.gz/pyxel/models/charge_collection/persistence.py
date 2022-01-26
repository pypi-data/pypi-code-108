#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""
Persistence module for the PyXel simulation.

This module is used in charge_collection

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| You          | charge_collection                | 05/20/2021                |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Name            | filename                            | -                   |
+-----------------+-------------------------------------+---------------------+

This module can be found in pyxel/models/charge_collection/persistence.py

Algorithm
=========

The persistence model take as input the total number of detrapped charges
(persistence map with a 10000 seconds soak at more than the FWC) and a map
which is the previous one divided by full well capacity. This gives the total
amount of trap per charge.

At each iteration of the pipeline, the model  will compute the amount of trapped charges in this iteration, add it
to the memory of the detector and then will remove this amount from the pixel array.


Code example
============

.. code-block:: python

    # To access the memory of the detector with the persistence map

    detector.persistence

Model reference in the YAML config file
=======================================

.. code-block:: yaml

pipeline:

  # Persistence model based on MOONS detector (H4RG) measurements
  - name: persistence
    func: pyxel.models.charge_collection.persistence
    enabled: true
    arguments:
      trap_time_constants: [1, 10, 100, 1000, 10000]
      trap_densities_filename: data/fits/20210408121614_20210128_ENG20370_AUTOCHAR-Persistence_FitTrapDensityMap.fits
      trap_capacities_filename: data/fits/20210408093114_20210128_ENG20370_AUTOCHAR-Persistence_FitMaximumTrapMap.fits
      trap_proportions: [0.307, 0.175, 0.188, 0.136, 0.194]

Useful links
============

Persistence paper from S. Tulloch
https://arxiv.org/abs/1908.06469

TO DO:
   - Add temperature dependency
   - Add default -flat?- trap maps

"""

import typing as t
from pathlib import Path

import numba
import numpy as np
from typing_extensions import Literal

from pyxel.data_structure import Persistence, SimplePersistence
from pyxel.detectors import CMOS
from pyxel.util import load_cropped_and_aligned_image


def simple_persistence(
    detector: CMOS,
    trap_time_constants: t.Sequence[float],
    trap_densities: t.Sequence[float],
    trap_capacities: t.Optional[t.Sequence[float]] = None,
) -> None:
    """Apply simple persistence model.

    Parameters
    ----------
    detector: CMOS
        Pyxel CMOS object.
    trap_time_constants: sequence of floats
        List of trap time constants.
    trap_densities: sequence of floats
        List of trap densities.
    trap_capacities: sequence of floats, optional
        List of trap capacities.
    """

    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a CMOS object for detector.")

    if not len(trap_time_constants) == len(trap_densities):
        raise ValueError(
            "Expecting same number of elements for parameters 'trap_time_constants'"
            "and 'trap_densities'"
        )

    if len(trap_time_constants) == 0:
        raise ValueError(
            "Expecting at least one 'trap_time_constants' and 'trap_densities'"
        )

    if trap_capacities is not None and not len(trap_capacities) == len(
        trap_time_constants
    ):
        raise ValueError(
            "Expecting same number of elements for parameters 'trap_capacities'"
            "and 'trap_time_constants'"
        )

    if not detector.has_persistence():
        detector.persistence = SimplePersistence(
            trap_time_constants=trap_time_constants,
            trap_densities=trap_densities,
            geometry=detector.pixel.shape,
        )

    if trap_capacities is None:
        fwc = None
    else:
        fwc = np.array(trap_capacities)

    new_pixel_array, new_all_trapped_charge = compute_simple_persistence(
        pixel_array=detector.pixel.array,
        all_trapped_charge=detector.persistence.trapped_charge_array,
        trap_densities=np.array(trap_densities),
        trap_time_constants=np.array(trap_time_constants),
        trap_capacities=fwc,
        delta_t=detector.time_step,
    )

    detector.pixel.array = new_pixel_array
    detector.persistence.trapped_charge_array = new_all_trapped_charge


@numba.njit(fastmath=True)
def compute_simple_persistence(
    pixel_array: np.ndarray,
    all_trapped_charge: np.ndarray,
    trap_densities: np.ndarray,
    trap_time_constants: np.ndarray,
    delta_t: float,
    trap_capacities: t.Optional[np.ndarray] = None,
) -> t.Tuple[np.ndarray, np.ndarray]:
    """Compute simple persistence.

    Parameters
    ----------
    pixel_array: ndarray
    all_trapped_charge: ndarray
    trap_densities: ndarray
    trap_time_constants: ndarray
    trap_capacities: ndarray, optional
    delta_t: float

    Returns
    -------
    tuple of ndarray
    """
    pixel_start = pixel_array.copy()

    for i, trapped_charge in enumerate(all_trapped_charge):
        # Computer trapped charge for this increment of time
        # Time factor is the integration time divided by the time constant (1, 10, 100, 1000, 10000)
        time_factor = delta_t / trap_time_constants[i]

        # Compute trapped charges
        available_traps = trap_densities[i] * pixel_array
        empty_traps = available_traps - trapped_charge
        diff = time_factor * empty_traps

        # maximum you can release is trapped_charge, max you can add is empty traps
        diff = clip_diff(
            diff=diff, trapped_charge=trapped_charge, empty_traps=empty_traps
        )

        trapped_charge += diff

        pixel_array -= diff

        all_trapped_charge[i] = trapped_charge

    pixel_diff = pixel_array - pixel_start

    for i, trapped_charge in enumerate(all_trapped_charge):

        if trap_capacities is None:
            fwc = None
        else:
            fwc = trap_capacities[i] * np.ones(trapped_charge.shape)

        densities = trap_densities[i] * np.ones(trapped_charge.shape)
        available_traps = pixel_array * densities

        trapped_charge_clipped, output_pixel = clip_trapped_charge(
            trapped_charge=trapped_charge,
            pixel=pixel_array,
            available_traps=available_traps,
            pixel_diff=pixel_diff,
            trap_capacities=fwc,
        )
        all_trapped_charge[i] = trapped_charge_clipped

    return output_pixel, all_trapped_charge


def persistence(
    detector: CMOS,
    trap_time_constants: t.Sequence[float],
    trap_proportions: t.Sequence[float],
    trap_densities_filename: t.Union[Path, str],
    trap_capacities_filename: t.Optional[t.Union[Path, str]] = None,
    trap_densities_position: t.Tuple[int, int] = (0, 0),
    trap_densities_align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
    trap_capacities_position: t.Tuple[int, int] = (0, 0),
    trap_capacities_align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
) -> None:
    """Apply persistence model.

    Parameters
    ----------
    detector: CMOS
        Pyxel CMOS object.
    trap_time_constants: sequence of floats
        A list of trap time constants.
    trap_proportions: sequence of floats
        A list of trap proportions.
    trap_densities_filename: path or str
        Path to densities file.
    trap_capacities_filename: path or str
        Path to capacities file.
    trap_densities_position: tuple of int
        Indices of starting row and column, used when fitting densities to detector.
    trap_densities_align: literal
        Keyword to align the densities to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    trap_capacities_position: tuple of int
        Indices of starting row and column, used when fitting capacities to detector.
    trap_capacities_align: literal
        Keyword to align the capacities to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    """

    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a CMOS object for detector.")

    if not len(trap_time_constants) == len(trap_proportions):
        raise ValueError(
            "Expecting same number of elements for parameters 'trap_time_constants'"
            "and 'trap_proportions'"
        )

    if len(trap_time_constants) == 0:
        raise ValueError(
            "Expecting at least one 'trap_time_constants' and 'trap_proportions'"
        )

    # If the file for trap density is correct open it and use it
    # otherwise I need to define a default trap density map
    shape = detector.pixel.shape
    densities_position_y, densities_position_x = trap_densities_position
    capacities_position_y, capacities_position_x = trap_capacities_position

    # Extract trap density / full well
    trap_densities_2d = load_cropped_and_aligned_image(
        shape=shape,
        filename=trap_densities_filename,
        position_x=densities_position_x,
        position_y=densities_position_y,
        align=trap_densities_align,
        allow_smaller_array=False,
    )

    if trap_capacities_filename is not None:

        # Extract the max amount of trap by long soak
        trap_capacities_2d = load_cropped_and_aligned_image(
            shape=shape,
            filename=trap_capacities_filename,
            position_x=capacities_position_x,
            position_y=capacities_position_y,
            align=trap_capacities_align,
            allow_smaller_array=False,
        )

        trap_capacities_2d[np.where(trap_capacities_2d < 0)] = 0

    else:
        trap_capacities_2d = None

    trap_densities_2d[np.where(trap_densities_2d < 0)] = 0
    trap_densities_2d = np.nan_to_num(
        trap_densities_2d, nan=0.0, posinf=0.0, neginf=0.0
    )

    if not np.all((0 <= trap_densities_2d) & (trap_densities_2d <= 1)):
        raise ValueError("Trap density map values not between 0 and 1.")

    if not detector.has_persistence():
        detector.persistence = Persistence(
            trap_time_constants=trap_time_constants,
            trap_proportions=trap_proportions,
            geometry=detector.pixel.shape,
        )

    new_pixel_array, new_all_trapped_charge = compute_persistence(
        pixel_array=detector.pixel.array,
        all_trapped_charge=detector.persistence.trapped_charge_array,
        trap_proportions=np.array(trap_proportions),
        trap_time_constants=np.array(trap_time_constants),
        trap_densities_2d=trap_densities_2d,
        trap_capacities_2d=trap_capacities_2d,
        delta_t=detector.time_step,
    )

    detector.pixel.array = new_pixel_array
    detector.persistence.trapped_charge_array = new_all_trapped_charge


@numba.njit(fastmath=True)
def compute_persistence(
    pixel_array: np.ndarray,
    all_trapped_charge: np.ndarray,
    trap_proportions: np.ndarray,
    trap_time_constants: np.ndarray,
    trap_densities_2d: np.ndarray,
    delta_t: float,
    trap_capacities_2d: t.Optional[np.ndarray] = None,
) -> t.Tuple[np.ndarray, np.ndarray]:
    """Compute persistence.

    Parameters
    ----------
    pixel_array: ndarray
    all_trapped_charge: ndarray
    trap_proportions: ndarray
    trap_time_constants: ndarray
    trap_densities_2d: ndarray
    delta_t: float
    trap_capacities_2d: ndarray, optional

    Returns
    -------
    tuple of ndarray
    """
    pixel_start = pixel_array.copy()

    for i, trapped_charge in enumerate(all_trapped_charge):

        # Computer trapped charge for this increment of time
        # Time factor is the integration time divided by the time constant (1, 10, 100, 1000, 10000)
        time_factor = delta_t / trap_time_constants[i]

        # Amount of charges trapped per unit of full well
        densities = trap_densities_2d * trap_proportions[i]

        # Compute trapped charges
        available_traps = densities * pixel_array
        empty_traps = available_traps - trapped_charge
        diff = time_factor * empty_traps

        # maximum you can release is trapped_charge, max you can add is empty traps
        diff = clip_diff(
            diff=diff, trapped_charge=trapped_charge, empty_traps=empty_traps
        )

        trapped_charge += diff

        pixel_array -= diff

        all_trapped_charge[i] = trapped_charge

    pixel_diff = pixel_array - pixel_start

    for i, trapped_charge in enumerate(all_trapped_charge):

        if trap_capacities_2d is None:
            fwc = None
        else:
            fwc = trap_capacities_2d * trap_proportions[i]

        densities = trap_densities_2d * trap_proportions[i]
        available_traps = pixel_array * densities

        trapped_charge_clipped, output_pixel = clip_trapped_charge(
            trapped_charge=trapped_charge,
            pixel=pixel_array,
            available_traps=available_traps,
            pixel_diff=pixel_diff,
            trap_capacities=fwc,
        )
        all_trapped_charge[i] = trapped_charge_clipped

    return output_pixel, all_trapped_charge


@numba.njit(fastmath=True)
def clip_trapped_charge(
    trapped_charge: np.ndarray,
    pixel: np.ndarray,
    available_traps: np.ndarray,
    pixel_diff: np.ndarray,
    trap_capacities: t.Optional[np.ndarray] = None,
) -> t.Tuple[np.ndarray, np.ndarray]:
    """Clip trapped charge between arrays of max and min value.

    Parameters
    ----------
    trapped_charge: ndarray
    pixel: ndarray
    available_traps: ndarray
    pixel_diff: ndarray
    trap_capacities: ndarray, optional

    Returns
    -------
    output: tuple of ndarray
    """

    n, m = trapped_charge.shape
    clipped = trapped_charge.copy()
    pixel_output = pixel.copy()

    for i in range(n):
        for j in range(m):
            if pixel_diff[i, j] < 0:
                if trap_capacities is not None:
                    maximum = min(available_traps[i, j], trap_capacities[i, j])
                else:
                    maximum = available_traps[i, j]
                if trapped_charge[i, j] > maximum:
                    clipped[i, j] = maximum

    pixel_output += trapped_charge - clipped

    return clipped, pixel_output


@numba.njit(fastmath=True)
def clip_diff(
    diff: np.ndarray, trapped_charge: np.ndarray, empty_traps: np.ndarray
) -> np.ndarray:
    """Clip diff array between arrays of min and max values.

    Parameters
    ----------
    diff: ndarray
    trapped_charge: ndarray
    empty_traps: ndarray

    Returns
    -------
    output: ndarray
    """
    n, m = diff.shape
    output = diff.copy()
    for i in range(n):
        for j in range(m):
            if diff[i, j] < 0:
                if diff[i, j] < -trapped_charge[i, j]:
                    output[i, j] = -trapped_charge[i, j]
            else:
                if diff[i, j] > empty_traps[i, j]:
                    output[i, j] = empty_traps[i, j]
    return output
