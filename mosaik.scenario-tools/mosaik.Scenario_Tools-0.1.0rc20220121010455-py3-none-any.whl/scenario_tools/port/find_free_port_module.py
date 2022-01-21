import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as \
            closing_socket:
        closing_socket.bind(('', 0))
        closing_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = closing_socket.getsockname()[1]

        return port
