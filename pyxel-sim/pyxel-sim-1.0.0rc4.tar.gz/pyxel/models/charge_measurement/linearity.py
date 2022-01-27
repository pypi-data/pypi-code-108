#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Linearity models."""
import typing as t

import numpy as np

from pyxel.detectors import Detector


def compute_poly_linearity(
    array_2d: np.ndarray,
    coefficients: t.Sequence[float],
) -> np.ndarray:
    """Add non-linearity to an array of values following a polynomial function.

    Parameters
    ----------
    array_2d: ndarray
        Input array.
    coefficients: list of float
        Coefficients of the polynomial function.

    Returns
    -------
    signal: np.ndarray
    """

    polynomial_function = np.polynomial.polynomial.Polynomial(coefficients)

    non_linear_signal = polynomial_function(array_2d)

    return non_linear_signal


def output_node_linearity_poly(
    detector: Detector,
    coefficients: t.Sequence[float],
) -> None:
    """.Add non-linearity to signal array to simulate the non-linearity of the output node circuit.

    The non-linearity is simulated by a polynomial function. The user specifies the polynomial coefficients.

    detector Signal unit: Volt

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    coefficients: list of float
        Coefficient of the polynomial function.
    """
    if len(coefficients) == 0:
        raise ValueError("Length of coefficient list should be more than 0.")

    signal_mean_array = detector.signal.array.astype("float64")
    signal_non_linear = compute_poly_linearity(
        array_2d=signal_mean_array, coefficients=coefficients
    )

    if np.any(signal_non_linear < 0):
        raise ValueError(
            "Signal array contains negative values after applying non-linearity model!"
        )

    detector.signal.array = signal_non_linear
