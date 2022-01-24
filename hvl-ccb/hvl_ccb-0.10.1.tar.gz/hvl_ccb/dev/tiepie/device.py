#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
TiePie devices.
"""

import logging

from .i2c import TiePieI2CHostMixin
from .generator import TiePieGeneratorMixin
from .oscilloscope import TiePieOscilloscope

logger = logging.getLogger(__name__)


class TiePieWS5(TiePieI2CHostMixin, TiePieGeneratorMixin, TiePieOscilloscope):
    """
    TiePie WS5 device.
    """


class TiePieHS5(TiePieI2CHostMixin, TiePieGeneratorMixin, TiePieOscilloscope):
    """
    TiePie HS5 device.
    """


class TiePieHS6(TiePieOscilloscope):
    """
    TiePie HS6 DIFF device.
    """
