#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock I2C host
"""
from libtiepie.i2chost import I2CHost as LtpI2CHost


class I2CHost(LtpI2CHost):
    """"""

    def __init__(self, serial_number):
        self._serial_number = serial_number
