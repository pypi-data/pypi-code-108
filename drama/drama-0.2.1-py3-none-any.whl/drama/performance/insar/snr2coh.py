"""Function that calculates the correlation coefficient as a function
of signal-to-noise ratio."""
import numpy as np


def coh_m(snr_1, snr_2=None, decibel=False):
    """coh_m calculates the correlation coefficient, also called
    the coherence, from finite SNR.

    Parameters
    ----------
    snr_1 : ndarray
        Signal-to-noise ratio of first interferometric channel
    snr_2 : ndarray
        Signal-to-noise ratio of second interferometric channel
        (Default value = None)
    decibel : bool
        True if values are given in dB (Default value = False)

    Returns
    -------
    ndarray
        correlation coefficient
    """
    if snr_2 is None:
        snr_2 = snr_1
    if decibel is False:
        correlation_coefficient = 1.0 / np.sqrt(
            np.dot(1 + 1.0 / snr_1, 1 + 1.0 / snr_2)
        )
    else:
        correlation_coefficient = 1.0 / np.sqrt(
            (1.0 + 10.0 ** -(snr_1 / 10.0)) * (1 + 10.0 ** -(snr_2 / 10.0))
        )
    return correlation_coefficient
