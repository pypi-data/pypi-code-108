#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple digitization."""


import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.models.readout_electronics.util import apply_gain_adc


def apply_simple_digitization(
    signal_2d: np.ndarray,
    gain_adc: float,
    min_clipped_value: float,
    max_clipped_value: float,
) -> np.ndarray:
    """Apply simple digitization.

    Parameters
    ----------
    signal_2d : ndarray
        2D signal to process. Unit: Volt
    gain_adc : float
        Gain of the analog-digital converter. Unit: adu/V
    min_clipped_value : float
        Minimum value to keep. Unit: adu
    max_clipped_value : float
        Maximum value to keep. Unit: adu

    Returns
    -------
    ndarray
    """
    # Gain of the Analog-Digital Converter
    image_2d = apply_gain_adc(signal_2d=signal_2d, gain_adc=gain_adc)

    # floor of signal values element-wise (quantization)
    image_quantized_2d = np.floor(image_2d)

    # convert floats to other datatype (e.g. 16-bit unsigned integers)
    image_clipped_2d = np.clip(
        image_quantized_2d,
        a_min=min_clipped_value,
        a_max=max_clipped_value,
    )

    return image_clipped_2d


def simple_digitization(
    detector: Detector,
    data_type: Literal["uint16", "uint32", "uint64", "uint"] = "uint16",
) -> None:
    """Digitize signal array mimicking readout electronics.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    data_type : str
        The desired data-type for the array. The data-type must be an signed or
        unsigned integer.
        Valid values: 'uint16', 'uint32', 'uint64', 'uint'
        Invalid values: 'int16', 'int32', 'int64', 'int', 'float'...
    """
    # Validation and Conversion stage
    # These steps will be probably moved into the YAML engine
    try:
        d_type = np.dtype(data_type)  # type: np.dtype
    except TypeError as ex:
        raise TypeError(
            "Can not locate the type defined as `data_type` argument in yaml file."
        ) from ex

    if not issubclass(d_type.type, np.integer):
        raise TypeError("Expecting a signed/unsigned integer.")

    image_2d = apply_simple_digitization(
        signal_2d=detector.signal.array,
        gain_adc=detector.characteristics.adc_gain,
        min_clipped_value=np.iinfo(d_type).min,
        max_clipped_value=np.iinfo(d_type).max,
    )

    detector.image.array = np.asarray(image_2d, dtype=d_type)
