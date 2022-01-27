"""Top-level module for gtunrealdevice.

"""
from gtunrealdevice.core import URDevice
from gtunrealdevice.core import create
from gtunrealdevice.core import connect
from gtunrealdevice.core import disconnect
from gtunrealdevice.core import execute
from gtunrealdevice.core import configure

from gtunrealdevice.config import version
from gtunrealdevice.config import edition

__version__ = version
__edition__ = edition

__all__ = [
    'URDevice',
    'create',
    'connect',
    'disconnect',
    'execute',
    'configure',
    'version',
    'edition',
]
