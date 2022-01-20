"""
pygsearch
~~~~~~~~~~
Python library to get google search results.
:copyright: (c) 2022-present Vitaman02
:license: MIT, see LICENSE for more details.
"""

from collections import namedtuple

from .gsearch import *


__title__ = "pygsearch"
__author__ = "Vitaman02"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Vitaman02"
__version__ = "0.3.7"


VersionInfo = namedtuple("VersionInfo", "major minor patch")

version_info = VersionInfo(*map(int, __version__.split(".")))
