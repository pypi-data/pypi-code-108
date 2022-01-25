import logging
import re
from typing import *
from typing import BinaryIO
from twopilabs.utils import usbtmc
from .scpi_transport_base import ScpiTransportBase
from .scpi_resource import ScpiResource
from .scpi_exceptions import ScpiTransportException


class ScpiUsbTmcTransport(ScpiTransportBase):
    _transport_class = 'ScpiUsbTmcTransport'
    _transport_info = 'USBTMC SCPI Transport'
    _transport_type = 'USBTMC'

    @classmethod
    def discover(cls, usb_vid: Optional[int] = None, usb_pid: Optional[int] = None) -> List[ScpiResource]:
        return [ScpiResource(transport=ScpiUsbTmcTransport,
                             location=device.location,
                             address=device.address,
                             name=None,
                             manufacturer=device.manufacturer,
                             model=device.product,
                             serialnum=device.serial_number,
                             info=device
                             ) for device in usbtmc.UsbTmcDevice.list_devices(usb_vid=usb_vid, usb_pid=usb_pid)]

    @classmethod
    def from_resource_name(cls, resource_name: str) -> Optional[ScpiResource]:
        m = re.match((
            r'^(?P<prefix>(?P<type>USB)(?P<board>\d+)?)'
            r'::(?P<vendor_id>((0x[0-9A-Fa-f]+)|([0-9]+)))'
            r'::(?P<product_id>((0x[0-9A-Fa-f]+)|([0-9]+)))'
            r'(::(?P<serial_number>[^\s:]+)?)?'
            r'(::(?P<interface_number>((0x[0-9A-Fa-f]+)|([0-9]+))))?'
            r'(::(?P<suffix>INSTR))?$'
        ), resource_name, re.IGNORECASE)

        if m is None:
            # Does not match the regex
            return None

        groupdict = m.groupdict()

        return ScpiResource(
            transport=ScpiUsbTmcTransport,
            address=usbtmc.UsbTmcDeviceAddress(
                vid=int(groupdict['vendor_id'], 0),
                pid=int(groupdict['product_id'], 0),
                serial_number=groupdict['serial_number'],
                interface_number=int(groupdict['interface_number'], 0) if groupdict['interface_number'] is not None else None
            )
        )

    @classmethod
    def to_resource_name(cls, resource: ScpiResource) -> str:
        address = resource.address
        return f'USB::0x{address.vid:04x}::0x{address.pid:04x}::' \
               + (f'{address.serial_number}' if address.serial_number is not None else '') \
               + (f'::{address.interface_number}' if address.interface_number is not None else '') \
               + '::INSTR'

    def __init__(self, address: usbtmc.UsbTmcDeviceAddress, timeout: float = 5, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)
        try:
            device = usbtmc.UsbTmcDevice(address=address, timeout=timeout, **kwargs)
        except usbtmc.UsbTmcException as msg:
            raise ScpiTransportException(msg) from msg

        self._io = cast(BinaryIO, device)
