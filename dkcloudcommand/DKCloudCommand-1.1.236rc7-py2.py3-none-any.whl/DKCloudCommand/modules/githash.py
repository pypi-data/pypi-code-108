#!/usr/bin/env python

from io import BytesIO
from hashlib import sha1
from sys import argv
from typing import Union

from DKCloudCommand.modules.DKFileHelper import DKFileHelper


class githash(object):
    def __init__(self) -> None:
        self.buf = BytesIO()

    def update(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            self.buf.write(data.encode("utf-8"))
        else:
            self.buf.write(data)

    def hexdigest(self) -> str:
        data = self.buf.getvalue()
        h = sha1()
        h.update(f"blob {len(data)}\0".encode("utf-8"))
        h.update(data)

        return h.hexdigest()


def githash_data(data: Union[str, bytes]) -> str:
    h = githash()
    h.update(data)
    return h.hexdigest()


def githash_by_file_name(file_name: str) -> str:
    file_contents = DKFileHelper.read_file(file_name)
    return githash_data(file_contents)


if __name__ == "__main__":
    for filename in argv[1:]:
        print(githash_by_file_name(filename))
