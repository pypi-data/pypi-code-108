#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock DeviceList
"""

from libtiepie.devicelist import DeviceList as LtpDeviceList

from .const import (
    MOCK_GENERATOR_SERIAL_NUMBER,
    MOCK_OSCILLOSCOPE_SERIAL_NUMBER,
    MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2,
    MOCK_I2CHOST_SERIAL_NUMBER,
    MOCK_DEVICE_SERIAL_NUMBER
)
from .devicelistitem import DeviceListItem


class DeviceList(LtpDeviceList):
    """"""

    def __init__(self):
        self.__clear_devices()

    # Enable mock patching with bool method used in the `update()` method
    def mock_devices(self):
        return True

    def __clear_devices(self):
        self._devices_by_serial_number = dict()
        self._devices_by_index = list()

    def __getitem__(self, index):
        return self._devices_by_index[index]

    def __len__(self):
        return self.count

    def __add_device(self, serial_number):
        item = DeviceListItem(serial_number)
        self._devices_by_serial_number[serial_number] = item
        self._devices_by_index.append(item)

    def get_item_by_serial_number(self, serial_number):
        return self._devices_by_serial_number[serial_number]

    def update(self):
        if self.mock_devices():
            self.__add_device(
                MOCK_DEVICE_SERIAL_NUMBER,
            )  # add device with oscilloscope, generator and I2C host
            self.__add_device(
                MOCK_OSCILLOSCOPE_SERIAL_NUMBER,
            )  # add device with oscilloscope only
            self.__add_device(
                MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2,
            )  # add device with oscilloscope only (without block measurement)
            self.__add_device(
                MOCK_GENERATOR_SERIAL_NUMBER,
            )  # add device with generator only
            self.__add_device(
                MOCK_I2CHOST_SERIAL_NUMBER,
            )  # add device with I2C host only
        else:
            self.__clear_devices()

    def _get_count(self):
        return len(self._devices_by_serial_number)

    count = property(_get_count)


device_list = DeviceList()
