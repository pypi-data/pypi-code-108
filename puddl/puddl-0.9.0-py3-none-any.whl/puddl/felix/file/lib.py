import socket
from pathlib import Path

from filetype import filetype


def default_device_name():
    return socket.gethostname()


def guess_filetype(path: Path):
    x = filetype.guess(str(path))
    if x is not None:
        return {
            "extension": x.extension,
            "mime": x.mime
        }


def get_stat(path: Path):
    s = path.stat()
    attrs = [a for a in dir(s) if a.startswith('st_')]
    return {a: getattr(s, a) for a in attrs}
