#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for "RS 232" and "Ethernet" interfaces, which are used to control power
supplies from Technix.
Manufacturer homepage:
https://www.technix-hv.com

The regulated power supplies series and capacitor chargers series from Technix are
series of low and high voltage direct current power supplies as well as capacitor
chargers.
The class `Technix` is tested with a CCR10KV-7,5KJ via an ethernet connection as well
as a CCR15-P-2500-OP via a serial connection.
Check the code carefully before using it with other devices or device series

This Python package may support the following interfaces from Technix:
    - `Remote Interface RS232
      <https://www.technix-hv.com/remote-interface-rs232.php>`_
    - `Ethernet Remote Interface
      <https://www.technix-hv.com/remote-interface-ethernet.php>`_
    - `Optic Fiber Remote Interface
      <https://www.technix-hv.com/remote-interface-optic-fiber.php>`_

"""

from .device import Technix, TechnixConfig  # noqa: F401
from .base import (  # noqa: F401
    TechnixError,
    TechnixSerialCommunicationConfig,
    TechnixSerialCommunication,
    TechnixTelnetCommunicationConfig,
    TechnixTelnetCommunication,
)
