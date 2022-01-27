#!/usr/bin/env python3
# coding: utf-8

import base64
import logging
import os

from joker.environ.utils import *  # noqa


# deprecated. use joker.environ.utils.check_{inclusive,exclusive}_* functions
def check_prefixes(string: str, include=None, exclude=None) -> bool:
    """
    Args:
        string (str): string to be checked
        include: None = include anything
        exclude: None = no exlusion rule
    """
    if exclude is not None:
        for prefix in exclude:
            if string.startswith(prefix):
                return False
    if include is not None:
        for prefix in include:
            if string.startswith(prefix):
                return True
        return False
    else:
        return True


def easylog(level):
    root = logging.root
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.setLevel(level)
    root.addHandler(handler)


def read_lines(path: str):
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        yield line


# Python 3.5+
if hasattr(bytes, 'hex'):
    def random_hex(length=12):
        return os.urandom(length).hex()
else:
    def random_hex(size=12):
        b = os.urandom(size)
        return base64.b16encode(b).decode('ascii')
