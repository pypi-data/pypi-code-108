import os
import sys
from psutil import process_iter

from waitress import serve
from .constants import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKER_COUNT


def validate_port_usage(port):
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == port:
                raise OSError(
                    f"Specified port '{port}' is already in use.")


def run(host, port, worker_count):

    validate_port_usage(port)

    import create_app
    serve(create_app.create(), host=host, port=port, threads=worker_count)


if __name__ == "__main__":
    run(DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKER_COUNT)
