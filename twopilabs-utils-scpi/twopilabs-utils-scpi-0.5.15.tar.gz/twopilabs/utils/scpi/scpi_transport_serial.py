import serial
import logging
import re
from typing import *
from typing import BinaryIO
from .scpi_transport_base import ScpiTransportBase
from .scpi_resource import ScpiResource
from .scpi_exceptions import ScpiTransportException

class ScpiSerialTransport(ScpiTransportBase):
    _transport_class = 'ScpiSerialTransport'
    _transport_info = 'Serial SCPI Transport'
    _transport_type = 'Serial'

    @classmethod
    def discover(cls, usb_vid: Optional[int] = None, usb_pid: Optional[int] = None) -> List[ScpiResource]:
        import serial.tools.list_ports

        return [ScpiResource(transport=ScpiSerialTransport,
                             location=f'{"usb" if port.pid is not None else "serial"}' + f':{port.location}' if port.location is not None else '',
                             address=port.device,
                             name=port.description,
                             manufacturer=port.manufacturer if port.manufacturer is not None else None,
                             model=port.product if port.product is not None else None,
                             serialnum=port.serial_number if port.serial_number is not None else None,
                             info=port
                             ) for port in serial.tools.list_ports.comports()
                if ((usb_vid is None) or (usb_vid == port.vid))
                and ((usb_pid is None) or (usb_pid == port.pid))]

    @classmethod
    def from_resource_name(cls, resource_name: str) -> Optional[ScpiResource]:
        m = re.match((
            r'^(?P<prefix>(?P<type>ASRL)(?P<board>[^\s:]+))'
            r'(::(?P<suffix>INSTR))?$'
        ), resource_name, re.IGNORECASE)

        if m is None:
            # Does not match the regex
            return None

        groupdict = m.groupdict()

        return ScpiResource(
            transport=ScpiSerialTransport,
            address=f'COM{int(groupdict["board"]):d}' if groupdict['board'].isnumeric() else groupdict['board']
        )

    @classmethod
    def to_resource_name(cls, resource: ScpiResource) -> str:
        address = resource.address.partition('COM')[2] if resource.address.startswith('COM') else resource.address
        return f'ASRL{address}::INSTR'

    def __init__(self, port: str, timeout: float = 5, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)
        try:
            port = serial.Serial(port=port, timeout=timeout, exclusive=True, **kwargs)
        except serial.SerialException as msg:
            raise ScpiTransportException(msg) from msg

        self._io = cast(BinaryIO, port)

        port.reset_input_buffer()
        port.reset_output_buffer()
        port.timeout = 0
        while port.read() != b'':
            pass
        port.timeout = timeout
