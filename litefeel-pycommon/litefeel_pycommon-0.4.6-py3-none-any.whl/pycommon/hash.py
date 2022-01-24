import hashlib
from typing import Callable


def file_sha1(filename: str) -> str:
    sha1 = hashlib.sha1()
    _update(filename, sha1.update)
    return sha1.hexdigest()


def file_md5(filename: str) -> str:
    md5 = hashlib.md5()
    _update(filename, md5.update)
    return md5.hexdigest()


def _update(filename: str, func: Callable[[bytes], None]):
    with open(filename, mode="rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            func(data)
