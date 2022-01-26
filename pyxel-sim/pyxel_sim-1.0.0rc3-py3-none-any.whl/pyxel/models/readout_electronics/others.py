#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout electronics model."""

import typing as t

from pyxel.detectors import MKID, Detector
from pyxel.models.readout_electronics.util import apply_gain_adc


def simple_processing(detector: Detector, gain_adc: t.Optional[float] = None) -> None:
    """Create a new image array (in adu) by applying the gain from the ADC (in adu/V) from the signal array.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    gain_adc: float
        Gain in units of ADU/V.
    """

    if gain_adc is None:
        final_gain = detector.characteristics.adc_gain
    else:
        final_gain = gain_adc

    # Apply gain from analog-to-digital converter
    new_image_2d = apply_gain_adc(signal_2d=detector.signal.array, gain_adc=final_gain)
    detector.image.array = new_image_2d


def simple_phase_conversion(detector: MKID, phase_conversion: float = 1.0) -> None:
    """Create an image array from phase array.

    Parameters
    ----------
    detector: MKID
        Pyxel MKID detector object.
    phase_conversion : float
        Phase conversion factor
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting a MKID object for the detector.")

    detector.image.array = phase_conversion * detector.phase.array
