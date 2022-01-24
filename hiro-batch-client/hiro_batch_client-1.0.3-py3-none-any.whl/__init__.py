"""
Package which contains the classes to communicate with HIRO Graph.
"""
import site
from os import path

from hiro_batch_client.batchclient import HiroGraphBatch, SessionData, AbstractIOCarrier, BasicFileIOCarrier, \
    SourceValueError, HiroResultCallback
from hiro_batch_client.version import __version__

this_directory = path.abspath(path.dirname(__file__))

__all__ = [
    'HiroGraphBatch', 'SessionData', 'HiroResultCallback',
    'AbstractIOCarrier', 'BasicFileIOCarrier', 'SourceValueError', '__version__'
]

site.addsitedir(this_directory)
