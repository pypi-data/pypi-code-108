#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""General purpose functions."""

import numpy as np


def apply_gain_adc(signal_2d: np.ndarray, gain_adc: float) -> np.ndarray:
    """Apply gain of the analog-digital converter.

    Parameters
    ----------
    signal_2d : ndarray
        Signal 2D data. Unit: Volt
    gain_adc : float
        Gain of the analog-digital converter. Unit: adu/V

    Returns
    -------
    ndarray
        A new 2D array. Unit: adu
    """
    return signal_2d * gain_adc
