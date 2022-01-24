#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""

import logging

from libtiepie import i2chost as ltp_i2c

from typing import (
    cast,
    Optional,
)

from .base import (
    TiePieDeviceType,
    _require_dev_handle,
    wrap_libtiepie_exception,
)
from .utils import PublicPropertiesReprMixin
from .oscilloscope import TiePieOscilloscope

logger = logging.getLogger(__name__)


class TiePieI2CHostConfigLimits:
    """
    Default limits for I2C host parameters.
    """

    def __init__(self, dev_i2c: ltp_i2c.I2CHost) -> None:
        # I2C Host
        pass


class TiePieI2CHostConfig(PublicPropertiesReprMixin):
    """
    I2C Host's configuration with cleaning of values in properties setters.
    """

    def __init__(self, dev_i2c: ltp_i2c.I2CHost):
        self.dev_i2c: ltp_i2c.I2CHost = dev_i2c
        self.param_lim: TiePieI2CHostConfigLimits = TiePieI2CHostConfigLimits(
            dev_i2c=dev_i2c
        )


class TiePieI2CHostMixin:
    """
    TiePie I2CHost sub-device.

    A wrapper for the `libtiepie.i2chost.I2CHost` class. To be mixed in with
    `TiePieOscilloscope` base class.
    """

    def __init__(self, com, dev_config):
        super().__init__(com, dev_config)

        self._i2c: Optional[ltp_i2c.I2CHost] = None

        self.config_i2c: Optional[TiePieI2CHostConfig] = None
        """
        I2C host's dynamical configuration.
        """

    @_require_dev_handle(TiePieDeviceType.I2C)
    def _i2c_config_setup(self) -> None:
        """
        Setup dynamical configuration for the connected I2C host.
        """
        self.config_i2c = TiePieI2CHostConfig(
            dev_i2c=self._i2c,
        )

    def _i2c_config_teardown(self) -> None:
        """
        Teardown dynamical configuration for the I2C Host.
        """
        self.config_i2c = None

    def _i2c_close(self) -> None:
        if self._i2c is not None:
            del self._i2c
            self._i2c = None

    def start(self) -> None:
        """
        Start the I2C Host.
        """
        super().start()  # type: ignore
        logger.info("Starting I2C host")

        self._i2c = cast(TiePieOscilloscope, self)._get_device_by_serial_number(
            TiePieDeviceType.I2C
        )
        self._i2c_config_setup()

    @wrap_libtiepie_exception
    def stop(self) -> None:
        """
        Stop the I2C host.
        """
        logger.info("Stopping I2C host")

        self._i2c_config_teardown()
        self._i2c_close()

        super().stop()  # type: ignore
