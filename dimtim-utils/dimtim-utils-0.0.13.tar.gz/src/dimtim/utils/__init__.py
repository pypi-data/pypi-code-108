import os
from io import BytesIO
from typing import Union


def noop(*args, **kwargs):  # noqa
    pass


def fileext(name: str):
    return os.path.splitext(name)[-1]


def named_bytesio(name: str, content: Union[str, bytes] = None):
    bio = BytesIO(content)
    bio.name = name
    return bio
