"""
TIM Python Client.
"""
from .tim import *
from . import _version

__version__ = _version.get_versions()['version']

from . import _version
__version__ = _version.get_versions()['version']
