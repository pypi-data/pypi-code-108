import socket


def from_hostname(name):
    hostname = socket.gethostname()
    return f"{name}@{hostname}"
