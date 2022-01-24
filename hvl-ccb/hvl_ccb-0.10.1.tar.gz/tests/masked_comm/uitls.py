#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
import socket


def get_free_tcp_port(host):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))
        addr, port = sock.getsockname()
    return port
