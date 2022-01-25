from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class SerialDevice:
    """A serial port device.

    Created by passing in a pyserial ListPortInfo and simplifies it.
    
    Attributes:
        name (str): The name of the interface
        manufacturer (str): The manufacturer of the device
        driver (str): The driver description
        vid (int): The registered vendor ID
        pid (int): The registered product ID
        serial_number (str): The serial number of the device

    """
    def __init__(self, port_info: ListPortInfo) -> None:
        self._name: str = port_info.device
        self._manufacturer: str = port_info.manufacturer
        self._driver: str = port_info.description
        self._vid: int = port_info.vid
        self._pid: int = port_info.pid
        self._serial_number: str = port_info.serial_number
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def manufacturer(self) -> str:
        return self._manufacturer
    
    @property
    def driver(self) -> str:
        return self._driver
    
    @property
    def vid(self) -> int:
        return self._vid
    
    @property
    def pid(self) -> int:
        return self._pid
    
    @property
    def serial_number(self) -> str:
        return self._serial_number


def is_valid(target: str) -> bool:
    """Validates a given serial port as available on the host.

    Args:
        target: Target port name e.g. ``/dev/ttyUSB0``
    
    Returns:
        True if found on the host.

    """
    devices = get_devices()
    for device in devices:
        if device.name == target:
            return True
    return False


def get_devices(target: str = None) -> list:
    """Returns a list of serial device information.
    
    Args:
        target: Optional device name to filter on.
    
    Returns:
        A list of `SerialDevice` objects describing each port.

    """
    devices = [SerialDevice(p) for p in list_ports.comports()]
    if target is not None:
        for device in devices:
            if device.name != target:
                devices.remove(device)
    return devices
