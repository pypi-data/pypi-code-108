#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`SAR` :term:`ADC` model."""
import numpy as np

from pyxel.detectors import Detector


def apply_sar_adc(
    signal_2d: np.ndarray,
    num_rows: int,
    num_cols: int,
    min_volt: float,
    max_volt: float,
    adc_bits: int,
) -> np.ndarray:
    """Apply :term:`SAR` :term:`ADC`.

    Parameters
    ----------
    signal_2d : ndarray
    num_rows : int
    num_cols : int
    min_volt : float
    max_volt : float
    adc_bits : int

    Returns
    -------
    ndarray
    """
    data_digitized_2d = np.zeros((num_rows, num_cols))

    # First normalize the data to voltage since there is no model for
    # the conversion photogenerated carrier > volts in the model/charge_measure
    signal_normalized_2d = signal_2d * max_volt / np.max(signal_2d)

    # Set the reference voltage of the ADC to half the max
    ref = max_volt / 2.0  # type: float

    # For each bits, compare the value of the ref to the capacitance value
    for i in np.arange(adc_bits):
        # digital value associated with this step
        digital_value = 2 ** (adc_bits - (i + 1))

        # All data that is higher than the ref is equal to the dig. value
        data_digitized_2d[signal_normalized_2d >= ref] += digital_value

        # Subtract ref value from the data
        signal_normalized_2d[signal_normalized_2d >= ref] -= ref

        # Divide reference voltage by 2 for next step
        ref /= 2.0

    return data_digitized_2d


# TODO: documentation, range volt - only max is used
def sar_adc(
    detector: Detector,
) -> None:
    """Digitize signal array using :term:`SAR` (Successive Approximation Register) :term:`ADC` logic.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    """

    min_volt, max_volt = detector.characteristics.adc_voltage_range
    adc_bits = detector.characteristics.adc_bit_resolution

    image_2d = apply_sar_adc(
        signal_2d=detector.signal.array,
        num_rows=detector.geometry.row,
        num_cols=detector.geometry.col,
        min_volt=min_volt,
        max_volt=max_volt,
        adc_bits=adc_bits,
    )  # type: np.ndarray

    detector.image.array = image_2d
