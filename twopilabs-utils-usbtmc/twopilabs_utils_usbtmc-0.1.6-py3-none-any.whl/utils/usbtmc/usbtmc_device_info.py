from typing import *
import usb.core
import usb.util
from .usbtmc_device_address import UsbTmcDeviceAddress
from .usbtmc_base import UsbTmcBase


class UsbTmcDeviceInfo(NamedTuple):
    manufacturer: str
    product: str
    serial_number: str
    address: UsbTmcDeviceAddress
    location: str
    
    @classmethod
    def from_device(cls, device: usb.core.Device) -> 'UsbTmcDeviceInfo':
        interfaces = []
        for cfg in device:
            interfaces.extend(usb.util.find_descriptor(
                    cfg,
                    find_all=True,
                    bInterfaceClass=UsbTmcBase.USBTMC_INTERFACE_CLASS,
                    bInterfaceSubClass=UsbTmcBase.USBTMC_INTERFACE_SUBCLASS))

        # Returns first interface found in configuration descriptors
        return cls(
            manufacturer=device.manufacturer,
            product=device.product,
            serial_number=device.serial_number,
            address=UsbTmcDeviceAddress(
                vid=device.idVendor,
                pid=device.idProduct,
                serial_number=device.serial_number,
                interface_number=interfaces[0].bInterfaceNumber),
            location=f'{device.bus}-{".".join([str(n) for n in device.port_numbers])}:{device.address}'
        )
