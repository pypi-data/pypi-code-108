#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple processing."""

import logging

from pyxel.detectors import Detector


def simple_processing(detector: Detector) -> None:
    """Create an image array from signal array.

    :param detector: Pyxel Detector object
    """
    logging.info("")
    detector.signal.array *= detector.characteristics.adc_gain
    detector.image.array = detector.signal.array
