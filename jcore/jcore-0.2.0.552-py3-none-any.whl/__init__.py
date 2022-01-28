# -*- coding: utf-8 -*-

"""
Twitch IRC & API Wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Twitch IRC channels and 
partial coverage of the Twitch API.
:copyright: (c) 2016-2021 Cubbei
:license: Restricted, direct inquiries to Cubbei.
"""

__title__ = 'Jarvis Core [Async]'
__author__ = 'cubbei'
__license__ = 'Restricted'
__copyright__ = 'Copyright 2016-2021 Cubbei'
__version__ = '0.2.0'

from collections import namedtuple

from .jsocket import Socket
from .client import Client
from .message import *



VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=2, micro=0, releaselevel='alpha', serial=0)
