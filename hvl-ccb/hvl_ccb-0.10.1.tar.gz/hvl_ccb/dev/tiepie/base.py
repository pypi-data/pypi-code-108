#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""

import time
import logging

import libtiepie as ltp
from libtiepie import generator as ltp_gen
from libtiepie import i2chost as ltp_i2c
from libtiepie import oscilloscope as ltp_osc
from libtiepie.exceptions import LibTiePieException, InvalidDeviceSerialNumberError

from hvl_ccb.dev.base import DeviceException
from ...configuration import configdataclass
from ...utils.typing import Number
from ...utils.enum import NameEnum

from functools import wraps
from typing import (
    Callable,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

logger = logging.getLogger(__name__)


@configdataclass
class TiePieDeviceConfig:
    """
    Configuration dataclass for TiePie
    """

    serial_number: int
    require_block_measurement_support: bool = True
    n_max_try_get_device: int = 10
    wait_sec_retry_get_device: Number = 1.0
    is_data_ready_polling_interval_sec: Number = 0.01

    def clean_values(self):
        if self.serial_number <= 0:
            raise ValueError("serial_number must be a positive integer.")
        if self.n_max_try_get_device <= 0:
            raise ValueError("n_max_try_get_device must be an positive integer.")
        if self.wait_sec_retry_get_device <= 0:
            raise ValueError("wait_sec_retry_get_device must be a positive number.")
        if self.is_data_ready_polling_interval_sec <= 0:
            raise ValueError(
                "is_data_ready_polling_interval_sec must be a positive number."
            )


class TiePieDeviceType(NameEnum, init="value ltp_class"):  # type:ignore
    """
    TiePie device type.
    """

    OSCILLOSCOPE = ltp.DEVICETYPE_OSCILLOSCOPE, ltp_osc.Oscilloscope
    I2C = ltp.DEVICETYPE_I2CHOST, ltp_i2c.I2CHost
    GENERATOR = ltp.DEVICETYPE_GENERATOR, ltp_gen.Generator


class TiePieError(DeviceException):
    """
    Error of the class TiePie
    """

    pass


def wrap_libtiepie_exception(func: Callable) -> Callable:
    """
    Decorator wrapper for `libtiepie` methods that use
    `libtiepie.library.check_last_status_raise_on_error()` calls.

    :param func: Function or method to be wrapped
    :raises TiePieError: instead of `LibTiePieException` or one of its subtypes.
    :return: whatever `func` returns
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LibTiePieException as e:
            logger.error(str(e), exc_info=e)
            raise TiePieError from e

    return wrapped_func


_LtpDeviceReturnType = TypeVar("_LtpDeviceReturnType")
"""
An auxiliary typing hint of a `libtiepie` device type for return value of
the `get_device_by_serial_number` function and the wrapper methods using it.
"""


@wrap_libtiepie_exception
def get_device_by_serial_number(
    serial_number: int,
    # Note: TiePieDeviceType aenum as a tuple to define a return value type
    device_type: Union[str, Tuple[int, _LtpDeviceReturnType]],
    n_max_try_get_device: int = 10,
    wait_sec_retry_get_device: float = 1.0,
) -> _LtpDeviceReturnType:
    """
    Open and return handle of TiePie device with a given serial number

    :param serial_number: int serial number of the device
    :param device_type: a `TiePieDeviceType` instance containing device identifier (int
        number) and its corresponding class, both from `libtiepie`, or a string name
        of such instance
    :param n_max_try_get_device: maximal number of device list updates (int number)
    :param wait_sec_retry_get_device: waiting time in seconds between retries (int
        number)
    :return: Instance of a `libtiepie`  device class according to the specified
        `device_type`
    :raises TiePieError: when there is no device with given serial number
    :raises ValueError: when `device_type` is not an instance of `TiePieDeviceType`
    """

    device_type = TiePieDeviceType(device_type)

    # include network search with ltp.device_list.update()
    ltp.network.auto_detect_enabled = True

    n_try = 0
    device_list_item: Optional[ltp.devicelistitem.DeviceListItem] = None
    while device_list_item is None and n_try < n_max_try_get_device:
        n_try += 1
        ltp.device_list.update()
        if not ltp.device_list:
            msg = f"Searching for device... (attempt #{n_try}/{n_max_try_get_device})"
            if n_try < n_max_try_get_device:
                logger.warning(msg)
                time.sleep(wait_sec_retry_get_device)
                continue
            msg = f"No devices found to start (attempt #{n_try}/{n_max_try_get_device})"
            logger.error(msg)
            raise TiePieError(msg)

        # if a device is found
        try:
            device_list_item = ltp.device_list.get_item_by_serial_number(serial_number)
        except InvalidDeviceSerialNumberError as e:
            msg = (
                f"The device with serial number {serial_number} is not "
                f"available; attempt #{n_try}/{n_max_try_get_device}."
            )
            if n_try < n_max_try_get_device:
                logger.warning(msg)
                time.sleep(wait_sec_retry_get_device)
                continue
            logger.error(str(e), exc_info=e)
            raise TiePieError from e
    assert device_list_item is not None

    if not device_list_item.can_open(device_type.value):
        msg = (
            f"The device with serial number {serial_number} has no "
            f"{device_type} available."
        )
        logger.error(msg)
        raise TiePieError(msg)

    return device_list_item.open_device(device_type.value)


def _verify_via_libtiepie(
    dev_obj: ltp.device.Device, verify_method_suffix: str, value: Number
) -> Number:
    """
    Generic wrapper for `verify_SOMETHING` methods of the `libtiepie` device.
    Additionally to returning a value that will be actually set,
    gives an warning.

    :param dev_obj: TiePie device object, which has the verify_SOMETHING method
    :param verify_method_suffix: `libtiepie` devices verify_SOMETHING method
    :param value: numeric value
    :returns: Value that will be actually set instead of `value`.
    :raises TiePieError: when status of underlying device gives an error
    """
    verify_method = getattr(
        dev_obj,
        f"verify_{verify_method_suffix}",
    )
    will_have_value = verify_method(value)
    if will_have_value != value:
        if verify_method_suffix == "record_length":
            value_str = f"{value:_d}"
            set_value = f"{will_have_value:_d}"
        else:
            value_str = f"{value:_.3f}"
            set_value = f"{will_have_value:_.3f}"
        msg = (
            f"Can't set {verify_method_suffix} to "
            f"{value_str}; instead {set_value} will be set."
        )
        logger.warning(msg)
    return will_have_value


def _require_dev_handle(device_type):
    """
    Create method decorator to check if the TiePie device handle is available.

    :param device_type: the TiePie device type which device handle is required
    :raises ValueError: when `device_type` is not an instance of `TiePieDeviceType`
    """

    device_type: TiePieDeviceType = TiePieDeviceType(device_type)

    def wrapper(method):
        """
        Method decorator to check if a TiePie device handle is available; raises
        `TiePieError` if hand is not available.

        :param method: `TiePieDevice` instance method to wrap
        :return: Whatever wrapped `method` returns
        """

        @wraps(method)
        def wrapped_func(self, *args, **kwargs):
            dev_str = None
            if device_type is TiePieDeviceType.OSCILLOSCOPE and self._osc is None:
                dev_str = "oscilloscope"
            if device_type is TiePieDeviceType.GENERATOR and self._gen is None:
                dev_str = "generator"
            if device_type is TiePieDeviceType.I2C and self._i2c is None:
                dev_str = "I2C host"
            if dev_str is not None:
                msg = f"The {dev_str} handle is not available; call `.start()` first."
                logger.error(msg)
                raise TiePieError(msg)
            return method(self, *args, **kwargs)

        return wrapped_func

    return wrapper
