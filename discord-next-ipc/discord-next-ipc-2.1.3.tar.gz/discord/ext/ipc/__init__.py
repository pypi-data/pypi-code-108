import collections

from discord.ext.ipc.client import Client
from discord.ext.ipc.server import Server
from discord.ext.ipc.errors import *

"""
A fork of the discontinued `discord.ext.ipc` project. This fork will continue it and still be maintained.

Docs will stay the same.
"""

_VersionInfo = collections.namedtuple("_VersionInfo", "major minor micro release serial")

version = "2.1.3"
version_info = _VersionInfo(2, 1, 3, "final", 0)
