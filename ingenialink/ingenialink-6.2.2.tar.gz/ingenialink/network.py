from enum import Enum
from abc import ABC, abstractmethod

from ._ingenialink import lib, ffi
from ingenialink.utils._utils import *

import ingenialogger
logger = ingenialogger.get_logger(__name__)


class NET_PROT(Enum):
    """Network Protocol."""
    EUSB = lib.IL_NET_PROT_EUSB
    MCB = lib.IL_NET_PROT_MCB
    ETH = lib.IL_NET_PROT_ETH
    ECAT = lib.IL_NET_PROT_ECAT
    CAN = 5


class NET_STATE(Enum):
    """Network State."""
    CONNECTED = lib.IL_NET_STATE_CONNECTED
    DISCONNECTED = lib.IL_NET_STATE_DISCONNECTED
    FAULTY = lib.IL_NET_STATE_FAULTY


class NET_DEV_EVT(Enum):
    """Device Event."""
    ADDED = lib.IL_NET_DEV_EVT_ADDED
    REMOVED = lib.IL_NET_DEV_EVT_REMOVED


class EEPROM_FILE_FORMAT(Enum):
    """EEPROM file format"""
    BINARY = 0
    INTEL = 1


class NET_TRANS_PROT(Enum):
    """Transmission protocol."""
    TCP = 1
    UDP = 2


@ffi.def_extern()
def _on_found_cb(ctx, servo_id):
    """On found callback shim."""
    self = ffi.from_handle(ctx)
    self._on_found(int(servo_id))


@ffi.def_extern()
def _on_evt_cb(ctx, evt, port):
    """On event callback shim."""
    self = ffi.from_handle(ctx)
    self._on_evt(NET_DEV_EVT(evt), pstr(port))


class Network(ABC):
    """Declaration of a general Network object."""
    def __init__(self):
        self.servos = []
        """list: List of the connected servos in the network."""

    @abstractmethod
    def scan_slaves(self):
        raise NotImplementedError

    @abstractmethod
    def connect_to_slave(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def disconnect_from_slave(self, servo):
        raise NotImplementedError

    @abstractmethod
    def load_firmware(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def subscribe_to_status(self, callback):
        raise NotImplementedError

    @abstractmethod
    def unsubscribe_from_status(self, callback):
        raise NotImplementedError

    @abstractmethod
    def start_status_listener(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def stop_status_listener(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def protocol(self):
        raise NotImplementedError


class NetworkMonitor:
    """Network Monitor.

    Args:
        prot (NET_PROT): Protocol.

    Raises:
        TypeError: If the protocol type is invalid.
        ILCreationError: If the monitor cannot be created.

    """
    def __init__(self, prot):
        if not isinstance(prot, NET_PROT):
            raise TypeError('Invalid protocol')

        mon = lib.il_net_dev_mon_create(prot.value)
        raise_null(mon)

        self._mon = ffi.gc(mon, lib.il_net_dev_mon_destroy)

    def start(self, on_evt):
        """Start the monitor.

        Args:
            on_evt (callback): Callback function.

        """
        self._on_evt = on_evt
        self._handle = ffi.new_handle(self)

        r = lib.il_net_dev_mon_start(self._mon, lib._on_evt_cb, self._handle)
        raise_err(r)

    def stop(self):
        """Stop the monitor."""
        lib.il_net_dev_mon_stop(self._mon)
