#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout noise model."""
import typing as t

import numpy as np

from pyxel.detectors import CMOS, Detector
from pyxel.util import temporary_random_state


def create_noise(signal_2d: np.ndarray, std_deviation: float) -> np.ndarray:
    """Create noise to signal array using normal random distribution.

    Parameters
    ----------
    signal_2d : ndarray
    std_deviation : float

    Returns
    -------
    ndarray
    """
    sigma_2d = std_deviation * np.ones_like(signal_2d)
    noise_2d = np.random.normal(loc=signal_2d, scale=sigma_2d)

    return noise_2d


def create_noise_cmos(
    signal_2d: np.ndarray,
    readout_noise: float,
    readout_noise_std: float,
    charge_readout_sensitivity: float,
) -> np.ndarray:
    """Create noise to signal array for :term:`CMOS` detectors.

    Parameters
    ----------
    signal_2d : ndarray
    readout_noise : float
    readout_noise_std : float
    charge_readout_sensitivity : float

    Returns
    -------
    ndarray
    """
    sigma_2d = np.random.normal(
        loc=readout_noise * charge_readout_sensitivity,
        scale=readout_noise_std * charge_readout_sensitivity,
        size=signal_2d.shape,
    )

    noise_2d = np.random.normal(loc=signal_2d, scale=sigma_2d)

    return noise_2d


@temporary_random_state
def output_node_noise(
    detector: Detector,
    std_deviation: float,
    seed: t.Optional[int] = None,
) -> None:
    """Add noise to signal array of detector output node using normal random distribution.

    Parameters
    ----------
    detector: Detector
        Pyxel detector object.
    std_deviation: float
        Standard deviation. Unit: V
    seed: int, optional
        Random seed.

    Raises
    ------
    ValueError
        Raised if 'std_deviation' is negative
    """
    if std_deviation < 0.0:
        raise ValueError("'std_deviation' must be positive.")

    noise_2d = create_noise(
        signal_2d=np.asarray(detector.signal.array, dtype=np.float64),
        std_deviation=std_deviation,
    )  # type: np.ndarray

    detector.signal.array = noise_2d


@temporary_random_state
def output_node_noise_cmos(
    detector: CMOS,
    readout_noise: float,
    readout_noise_std: float,
    seed: t.Optional[int] = None,
) -> None:
    """Output node noise model for :term:`CMOS` detectors where readout is statistically independent for each pixel.

    Parameters
    ----------
    detector: CMOS
        Pyxel :term:`CMOS` object.
    readout_noise: float
        Mean readout noise for the array in units of electrons. Unit: electron
    readout_noise_std: float
        Readout noise standard deviation in units of electrons. Unit: electron
    seed: int, optional
        Random seed.

    Raises
    ------
    TypeError
        Raised if the 'detector' is not a :term:`CMOS` object.
    ValueError
        Raised if 'readout_noise_std' is negative.
    """
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    if readout_noise_std < 0.0:
        raise ValueError("'readout_noise_std' must be positive.")

    noise_2d = create_noise_cmos(
        signal_2d=np.asarray(detector.signal.array, dtype=np.float64),
        readout_noise=readout_noise,
        readout_noise_std=readout_noise_std,
        charge_readout_sensitivity=detector.characteristics.charge_to_volt_conversion,
    )  # type: np.ndarray

    detector.signal.array = noise_2d
