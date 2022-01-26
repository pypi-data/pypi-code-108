#!/usr/bin/env python

import os


def abspath(_path: str):
    _path.lstrip('/tmp')
    return os.path.join('/tmp', _path)
