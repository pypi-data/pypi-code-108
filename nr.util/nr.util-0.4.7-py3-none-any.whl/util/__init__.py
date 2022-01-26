
""" General purpose utility library. """

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = "0.4.7"

from ._chaindict import ChainDict
from ._coalesce import coalesce
from ._optional import Optional
from ._orderedset import OrderedSet
from ._refreshable import Refreshable
from ._stream import Stream

__all__ = ['ChainDict', 'coalesce', 'Optional', 'OrderedSet', 'Refreshable', 'Stream']
