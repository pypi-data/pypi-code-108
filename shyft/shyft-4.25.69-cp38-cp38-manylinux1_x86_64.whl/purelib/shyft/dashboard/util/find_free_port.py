import socket
from contextlib import closing


def find_free_port():
    """from SO https://stackoverflow.com/questions/1365265/on-localhost-how-to-pick-a-free-port-number
    available port number for use
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]