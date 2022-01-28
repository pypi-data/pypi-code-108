from .entry import Entry, BASE_URL, MAX_SIZE
from .exceptions import *
from .client import AxewClient

__version__ = "1.0.7"

import logging
from collections import namedtuple

logging.getLogger(__name__).addHandler(logging.NullHandler())
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=0, micro=7, releaselevel="final", serial=0)
