from typing import *

class UsbTmcDeviceAddress(NamedTuple):
    vid: int
    pid: int
    serial_number: Optional[str]
    interface_number: Optional[int]
    
