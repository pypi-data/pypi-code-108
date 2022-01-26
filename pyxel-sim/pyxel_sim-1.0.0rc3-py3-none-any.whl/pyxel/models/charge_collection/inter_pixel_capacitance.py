#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Simple Inter Pixel Capacitance model: https://iopscience.iop.org/article/10.1088/1538-3873/128/967/095001/pdf."""

import numpy as np
from astropy.convolution import convolve_fft

from pyxel.detectors import CMOS


def ipc_kernel(
    coupling: float, diagonal_coupling: float = 0.0, anisotropic_coupling: float = 0.0
) -> np.ndarray:
    """Return the IPC convolution kernel from the input coupling parameters.

    Parameters
    ----------
    coupling: float
    diagonal_coupling: float
    anisotropic_coupling: float

    Returns
    -------
    kernel: np.ndarray
    """

    if not diagonal_coupling < coupling:
        raise ValueError("Requirement diagonal_coupling <= coupling is not met.")
    if not anisotropic_coupling < coupling:
        raise ValueError("Requirement anisotropic_coupling <= coupling is not met.")
    if not 0 <= coupling + diagonal_coupling <= 0.25:
        raise ValueError("Requirement coupling + diagonal_coupling << 1 is not met.")

    kernel = np.array(
        [
            [diagonal_coupling, coupling - anisotropic_coupling, diagonal_coupling],
            [
                coupling + anisotropic_coupling,
                1 - 4 * (coupling + diagonal_coupling),
                coupling + anisotropic_coupling,
            ],
            [diagonal_coupling, coupling - anisotropic_coupling, diagonal_coupling],
        ],
        dtype=float,
    )

    return kernel


def compute_ipc_convolution(
    input: np.ndarray,
    coupling: float,
    diagonal_coupling: float,
    anisotropic_coupling: float,
) -> np.ndarray:
    """Compute convolution of the array with IPC kernel.

    Parameters
    ----------
    input: ndarray
    coupling: float
    diagonal_coupling: float
    anisotropic_coupling: float

    Returns
    -------
    array: ndarray
    """
    kernel = ipc_kernel(
        coupling=coupling,
        diagonal_coupling=diagonal_coupling,
        anisotropic_coupling=anisotropic_coupling,
    )

    # Convolution, extension on the edges with the mean value
    mean = np.mean(input)
    array = convolve_fft(input, kernel, boundary="fill", fill_value=mean)

    return array


def simple_ipc(
    detector: "CMOS",
    coupling: float,
    diagonal_coupling: float = 0.0,
    anisotropic_coupling: float = 0.0,
) -> None:
    """Convolve pixel array with the IPC kernel.

    Parameters
    ----------
    detector: CMOS
    coupling: float
    diagonal_coupling: float
    anisotropic_coupling: float

    Returns
    -------
    None
    """
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a CMOS object for detector.")

    array = compute_ipc_convolution(
        input=detector.pixel.array,
        coupling=coupling,
        diagonal_coupling=diagonal_coupling,
        anisotropic_coupling=anisotropic_coupling,
    )

    detector.pixel.array = array
