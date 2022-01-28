import warnings
from typing import Union

import numpy as np
import pandas as pd

try:
    from uncertainties import umath, core

    UNCERTAINTIES = True
except ImportError:
    UNCERTAINTIES = False


def to_lin(data):
    return 10 ** (data / 10.0)


def from_lin(data):
    if UNCERTAINTIES and isinstance(data, (core.Variable, core.AffineScalarFunc)):
        log10 = umath.log10  # pylint: disable=no-member
    else:
        log10 = np.log10
    return 10 * log10(data)


def mean(data, axis=None):
    return from_lin(np.mean(to_lin(data), axis=axis))


def subtract(
    signal: Union[pd.DataFrame, np.ndarray, float],
    noise: Union[pd.DataFrame, np.ndarray, float],
) -> Union[pd.DataFrame, np.ndarray, float]:
    """Subtract noise from the signal.

    Both signal and noise are converted from logarithmic scale to linear,
    then subtracted and converted back to logarithmic scale.

    Parameters
    ----------
    signal
    noise

    Returns
    -------

    """
    if isinstance(signal, pd.DataFrame):
        return from_lin(
            pd.DataFrame.subtract(to_lin(signal), to_lin(noise), axis="index")
        )
    return from_lin(to_lin(signal) - to_lin(noise))


def average(datasets):
    warnings.warn(
        "Use `openqlab.conversion.de.mean` with argument 'axis=-1' instead",
        DeprecationWarning,
    )
    lin = to_lin(datasets)
    average = np.sum(lin, 0) / len(lin)
    return from_lin(average)


def dBm2Vrms(dbm, R=50.0):
    return np.sqrt(0.001 * R) * 10 ** (dbm / 20)
