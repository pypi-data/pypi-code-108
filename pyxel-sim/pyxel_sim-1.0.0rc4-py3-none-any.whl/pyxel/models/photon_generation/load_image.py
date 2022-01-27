#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models."""
import typing as t

from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image


def load_image(
    detector: Detector,
    image_file: str,
    position: t.Tuple[int, int] = (0, 0),
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
    convert_to_photons: bool = False,
    multiplier: float = 1.0,
    time_scale: float = 1.0,
    bit_resolution: t.Optional[int] = None,
) -> None:
    r"""Load FITS file as a numpy array and add to the detector as input image.

    Parameters
    ----------
    detector: Detector
    image_file: str
        Path to image file.
    position: tuple
        Indices of starting row and column, used when fitting image to detector.
    align: Literal
        Keyword to align the image to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    convert_to_photons: bool
        If ``True``, the model converts the values of loaded image array from ADU to
        photon numbers for each pixel using the Photon Transfer Function:
        :math:`PTF = quantum\_efficiency \cdot charge\_to\_voltage\_conversion
        \cdot pre\_amplification \cdot adc\_factor`.
    multiplier: float
        Multiply photon array level with a custom number.
    time_scale: float
        Time scale of the photon flux, default is 1 second. 0.001 would be ms.
    bit_resolution: int
        Bit resolution of the loaded image.
    """

    shape = (detector.geometry.row, detector.geometry.col)
    position_y, position_x = position

    image = load_cropped_and_aligned_image(
        filename=image_file,
        shape=shape,
        align=align,
        position_x=position_x,
        position_y=position_y,
    )

    detector.input_image = image
    photon_array = image

    if convert_to_photons:

        if not bit_resolution:
            raise ValueError(
                "Bit resolution of the input image has to be specified for converting to photons."
            )

        cht = detector.characteristics
        adc_multiplier = cht.adc_voltage_range[1] / 2 ** bit_resolution

        photon_array = (
            photon_array
            * adc_multiplier
            / (
                cht.quantum_efficiency
                * cht.charge_to_volt_conversion
                * cht.pre_amplification
            )
        )
    photon_array = photon_array * (detector.time_step / time_scale) * multiplier

    try:
        detector.photon.array += photon_array
    except ValueError as ex:
        raise ValueError("Shapes of arrays do not match") from ex
