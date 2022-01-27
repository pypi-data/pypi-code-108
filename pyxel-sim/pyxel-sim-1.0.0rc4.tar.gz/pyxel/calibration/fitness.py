#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fitness functions for model fitting."""

import numba
import numpy as np


@numba.njit
def sum_of_abs_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    diff = target - simulated
    diff *= weighting

    result = float(np.sum(np.abs(diff)))
    return result


@numba.njit
def sum_of_squared_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    diff = target - simulated
    diff_square = diff * diff
    diff_square *= weighting

    result = float(np.sum(diff_square))
    return result
