
# -*- coding: utf-8 -*-

from .edge2client import Edge2Client
import os

version = {}
with open(os.path.join(os.path.dirname(__file__), "version.py")) as fp:
    exec(fp.read(), version)

__version__ = version['__version__']
__title__ = 'edge2client'
__copyright__ = 'Copyright 2020 OpenResty Inc.'

__all__ = [
    'Edge2Client', '__version__'
]
