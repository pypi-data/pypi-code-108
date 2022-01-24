#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock TCP servers
"""

import socket
import time

from hvl_ccb.dev import lauda


class FakeTCP:
    """
    Class implementing a mock TCP server
    """

    def __init__(self, _SOCK_TIMEOUT):
        self._SOCK_TIMEOUT = _SOCK_TIMEOUT

    def run_fake_server(self, host, port, term="\r\n", wait_sec_rw=0.005):
        # Run a server to listen for a connection and then close it
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.settimeout(self._SOCK_TIMEOUT)
            server_sock.bind((host, port))
            server_sock.listen(0)
            connection, client_address = server_sock.accept()
            with connection:
                # Receive the data and retransmit it
                while True:
                    data = connection.recv(64)
                    if not data:
                        break
                    parsed = data.decode("ascii")
                    if "TYPE" in parsed:
                        connection.sendall(bytes(f"RP245 PRO{term}", "ascii"))
                    elif "IN_PV_00" in parsed:
                        connection.sendall(bytes(f"OK{term}25.00{term}", "ascii"))
                    elif "FOO" in parsed:
                        connection.sendall(bytes(f"ERR01{term}", "ascii"))
                    elif (
                        parsed == f"{lauda.LaudaProRp245eCommand.STOP}{term}"
                        or "end" in parsed
                    ):
                        connection.sendall(data)
                        break
                    else:
                        connection.sendall(data)
                    time.sleep(min(wait_sec_rw, self._SOCK_TIMEOUT / 5))
                # close the connection in a timely fashion => call shutdown before close
                connection.shutdown(socket.SHUT_RDWR)

    def run_bad_fake_server(self, host, port, term="\r\n", wait_sec_rw=0.005):
        # Run a server to listen for a connection and then close it
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.settimeout(self._SOCK_TIMEOUT)
            server_sock.bind((host, port))
            server_sock.listen(0)
            connection, client_address = server_sock.accept()
            with connection:
                # Receive the data and retransmit it
                while True:
                    data = connection.recv(64)
                    if not data:
                        break
                    parsed = data.decode("ascii")
                    if "TYPE" in parsed:
                        connection.sendall(
                            bytes(f"Chuck Norris was here{term}", "ascii")
                        )
                    elif (
                        parsed == f"{self.chiller.LaudaProRp245eCommand.STOP}{term}"
                        or "end" in parsed
                    ):
                        connection.sendall(data)
                        break
                    else:
                        connection.sendall(data)
                    time.sleep(min(wait_sec_rw, self._SOCK_TIMEOUT / 5))
                # close the connection in a timely fashion => call shutdown before close
                connection.shutdown(socket.SHUT_RDWR)
