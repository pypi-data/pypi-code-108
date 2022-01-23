# -*- coding: utf-8 -*-
"""Module containing a classes to abstract the socket
"""
# import basic stuff
import socket
import select
import logging
import time
import sys
import socks  # type: ignore
import urllib.parse
from typing import Tuple, Optional

# import own stuff
import tlsmate.config as conf
import tlsmate.recorder as rec
import tlsmate.resolver as resolver
import tlsmate.structs as structs
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff


class Socket(object):
    """Class implementing the socket interface.

    Arguments:
        tlsmate: the application object
    """

    def __init__(self, config: conf.Configuration, recorder: rec.Recorder) -> None:
        self._socket: Optional[socks.socksocket] = None
        self._config = config
        self._recorder = recorder
        self._fragment_max_size = 16384

    def open_socket(self, l4_addr: structs.TransportEndpoint) -> None:
        """Opens a socket.

        Arguments:
            l4_addr: The L4-endpoint, consisting of the IP-address and the
                port.
        """

        addr_info: Tuple
        if l4_addr.host_type is tls.HostType.HOST:
            l4_addr = resolver.get_ip_endpoint(
                l4_addr,
                proxy=self._config.get("proxy"),
                ipv6_preference=self._config.get("ipv6_preference"),
            )

        addr_info = (l4_addr.host, l4_addr.port)
        family = (
            socket.AF_INET
            if l4_addr.host_type is tls.HostType.IPV4
            else socket.AF_INET6
        )

        if self._recorder.is_injecting():
            return

        try:
            self._socket = socks.socksocket(family, socket.SOCK_STREAM)
            proxy = self._config.get("proxy")
            if proxy:
                parsed = urllib.parse.urlparse(proxy)
                self._socket.set_proxy(socks.HTTP, parsed.hostname, parsed.port)
            self._socket.settimeout(5.0)
            self._socket.connect(addr_info)
            self._socket.settimeout(None)
            addr = self._socket.getsockname()
            laddr = addr[0]
            lport = addr[1]
            addr = self._socket.getpeername()
            raddr = addr[0]
            rport = addr[1]

        except OSError:
            utils.exit_with_error(f"Cannot open TCP connection to {l4_addr}")

        if self._config.get("progress"):
            sys.stderr.write(".")
            sys.stderr.flush()

        logging.info(f"{utils.Log.time()}: Socket opened")
        logging.info(f"local address: {laddr}:{lport}")
        logging.info(f"remote address: {raddr}:{rport}")

    def close_socket(self) -> None:
        """Closes a socket.
        """

        if self._socket is not None:
            logging.info(f"{utils.Log.time()}: closing socket")
            self._socket.close()
            self._socket = None

    def sendall(self, data: bytes) -> None:
        """Sends data to the network.

        Arguments:
            data: The data to send.
        """

        cont = self._recorder.trace_socket_sendall(data)
        if cont:
            if self._socket is None:
                return

            self._socket.sendall(data)

    def recv_data(self, timeout: float = 5) -> bytes:
        """Wait for data from the network.

        Arguments:
            timeout: The maximum time to wait in seconds.

        Returns:
            The bytes received or None if the timeout expired.

        Raises:
            TlsMsgTimeoutError: If no data is received within the given timeout
            TlsConnectionClosedError: If the connection was closed.
        """

        data = self._recorder.inject_socket_recv()
        if data is None:
            assert self._socket

            start = time.time()
            rfds, wfds, efds = select.select([self._socket], [], [], timeout)
            timeout = time.time() - start
            if not rfds:
                self._recorder.trace_socket_recv(timeout, rec.SocketEvent.TIMEOUT)
                raise tls.TlsMsgTimeoutError

            try:
                data = self._socket.recv(self._fragment_max_size)

            except ConnectionResetError as exc:
                self._recorder.trace_socket_recv(timeout, rec.SocketEvent.CLOSURE)
                self.close_socket()
                raise tls.TlsConnectionClosedError(exc)

            self._recorder.trace_socket_recv(timeout, rec.SocketEvent.DATA, data=data)
        if data == b"":
            self.close_socket()
            raise tls.TlsConnectionClosedError()

        return data
