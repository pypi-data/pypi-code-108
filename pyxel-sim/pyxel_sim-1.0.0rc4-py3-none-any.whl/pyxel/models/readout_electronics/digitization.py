#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout electronics model."""
import logging

import numpy as np

from pyxel.detectors import MKID, Detector

# from astropy import units as u


# TODO: Fix this
# @validators.validate
# @config.argument(name='data_type', label='type of output data array', units='ADU',
#                  validate=checkers.check_choices(['numpy.uint16', 'numpy.uint32', 'numpy.uint64',
#                                                   'numpy.int32', 'numpy.int64']))
def simple_digitization(detector: MKID, data_type: str = "uint16") -> None:
    """Digitize signal array mimicking readout electronics.

    :param detector: Pyxel Detector object
    :param data_type: numpy integer type: ``numpy.uint16``, ``numpy.uint32``, ``numpy.uint64``,
                                          ``numpy.int32``, ``numpy.int64``
    """
    logging.info("")

    try:
        d_type = np.dtype(data_type)  # type: np.dtype
    except TypeError as ex:
        raise TypeError(
            "Can not locate the type defined as `data_type` argument in yaml file."
        ) from ex

    # Gain of the Analog-Digital Converter
    detector.signal.array *= detector.characteristics.adc_gain

    # floor of signal values element-wise (quantization)
    detector.signal.array = np.floor(detector.signal.array)

    # convert floats to other datatype (e.g. 16-bit unsigned integers)
    result = np.asarray(
        np.clip(
            detector.signal.array,
            a_min=np.iinfo(d_type).min,
            a_max=np.iinfo(d_type).max,
        )
    )  # type: np.ndarray

    detector.signal.array = result
    detector.image.array = np.asarray(detector.signal.array, dtype=d_type)


def simple_processing(detector: Detector) -> None:
    """Create an image array from signal array.

    :param detector: Pyxel Detector object
    """
    logging.info("")
    detector.signal.array *= detector.characteristics.adc_gain
    detector.image.array = detector.signal.array


def basic_processing(detector: Detector) -> None:
    """Create an image array from signal array.

    :param detector: Pyxel Detector object
    """

    detector.image.array = detector.signal.array


def phase_conversion(detector: MKID) -> None:
    """Create an image array from phase array.

    :param detector: Pyxel Detector object
    """

    detector.image.array = detector.phase.array


def sar_adc(detector: Detector, adc_bits: int = 16, range_volt: tuple = (0, 5)) -> None:
    """Digitize signal array using SAR ADC logic.

    :param detector: Pyxel Detector object
    :param adc_bits: integer: Number of bits for the ADC
    :param range_volt: tuple with min anx max volt value
    """
    # import numpy as np
    logging.info("")
    # Extract the data to digitize
    data = detector.signal.array
    data_digitized = np.zeros((detector.geometry.row, detector.geometry.col))
    # First normalize the data to voltage since there is no model for
    # the conversion photogenerated carrier > volts in the model/charge_measure
    data = data * range_volt[1] / np.max(data)
    # steps = list()
    # Set the reference voltage of the ADC to half the max
    ref = range_volt[1] / 2.0
    # For each bits, compare the value of the ref to the capacitance value
    for i in np.arange(0, adc_bits):
        # digital value associated with this step
        digital_value = 2 ** (adc_bits - (i + 1))
        # All data that is higher than the ref is equal to the dig. value
        data_digitized[data >= ref] += digital_value
        # Subtract ref value from the data
        data[data >= ref] -= ref
        # steps.append(ref)
        # Divide reference voltage by 2 for next step
        ref /= 2.0

    detector.image.array = data_digitized
    # return data_digitized, steps
