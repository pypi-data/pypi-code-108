from time import sleep
from threading import Thread
from abc import ABC, abstractmethod
from .._ingenialink import lib, ffi
from ingenialink.network import Network, NET_DEV_EVT, NET_STATE
from ingenialink.exceptions import ILError

import ingenialogger
logger = ingenialogger.get_logger(__name__)


class NetStatusListener(Thread):
    """Network status listener thread to check if the drive is alive.

    Args:
        network (IPBNetwork): Network instance of the IPB communication.

    """

    def __init__(self, network):
        super(NetStatusListener, self).__init__()
        self.__net = network
        self.__stop = False

    def run(self):
        status = self.__net.status
        while not self.__stop:
            if status != self.__net.status:
                if self.__net.status == NET_STATE.CONNECTED.value:
                    self.__net._notify_status(NET_DEV_EVT.ADDED)
                elif self.__net.status == NET_STATE.DISCONNECTED.value:
                    self.__net._notify_status(NET_DEV_EVT.REMOVED)
                status = self.__net.status
            sleep(1)

    def stop(self):
        self.__stop = True


class IPBNetwork(Network, ABC):
    """IPB Network defines a general class for all IPB based communications."""
    def __init__(self):
        super(IPBNetwork, self).__init__()
        self._cffi_network = None
        """CFFI instance of the network."""

        self.__observers_net_state = []
        self.__listener_net_status = None

    def _create_cffi_network(self, cffi_network):
        """Create a new class instance from an existing network.

        Args:
            cffi_network (CData): Instance to copy.

        """
        self._cffi_network = ffi.gc(cffi_network, lib.il_net_fake_destroy)

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

    def close_socket(self):
        """Closes the established network socket."""
        return lib.il_net_close_socket(self._cffi_network)

    def destroy_network(self):
        """Destroy network instance."""
        lib.il_net_destroy(self._cffi_network)

    def subscribe_to_status(self, callback):
        """Calls given function everytime a connection/disconnection event is
        raised.

        Args:
            callback (function): Function that will be called every time an event
                is raised.

        """
        if callback in self.__observers_net_state:
            logger.info('Callback already subscribed.')
            return
        self.__observers_net_state.append(callback)

    def unsubscribe_from_status(self, callback):
        """Unsubscribe from state changes.

        Args:
            callback (function): Callback function.

        """
        if callback not in self.__observers_net_state:
            logger.info('Callback not subscribed.')
            return
        self.__observers_net_state.remove(callback)

    def _notify_status(self, status):
        for callback in self.__observers_net_state:
            callback(status)

    def _set_status_check_stop(self, stop):
        """Start/Stop the internal monitor of the drive status.

        Args:
            stop (int): 0 to START, 1 to STOP.

        Raises:
            ILError: If the operation returns a negative error code.

        """
        r = lib.il_net_set_status_check_stop(self._cffi_network, stop)

        if r < 0:
            raise ILError('Could not start servo monitoring')

    def start_status_listener(self):
        """Start monitoring network events (CONNECTION/DISCONNECTION)."""
        self._set_status_check_stop(0)
        if not self.__listener_net_status:
            self.__listener_net_status = NetStatusListener(self)
            self.__listener_net_status.start()

    def stop_status_listener(self):
        """Stop monitoring network events (CONNECTION/DISCONNECTION)."""
        self._set_status_check_stop(1)
        if self.__listener_net_status is not None and \
                self.__listener_net_status.is_alive():
            self.__listener_net_status.stop()
            self.__listener_net_status.join()
        self.__listener_net_status = None

    def set_reconnection_retries(self, retries):
        """Set the number of reconnection retries in our application.

        Args:
            retries (int): Number of reconnection retries.

        """
        return lib.il_net_set_reconnection_retries(self._cffi_network, retries)

    def set_recv_timeout(self, timeout):
        """Set receive communications timeout.

        Args:
            timeout (int): Timeout in ms.
        Returns:
            int: Result code.

        """
        return lib.il_net_set_recv_timeout(self._cffi_network, timeout*1000)

    @property
    def protocol(self):
        raise NotImplementedError

    @property
    def status(self):
        """NET_STATE: Obtain network status"""
        return lib.il_net_status_get(self._cffi_network)
