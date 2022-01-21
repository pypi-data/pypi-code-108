'''_5820.py

ConnectedComponentType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONNECTED_COMPONENT_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'ConnectedComponentType')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectedComponentType',)


class ConnectedComponentType(Enum):
    '''ConnectedComponentType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONNECTED_COMPONENT_TYPE

    __hash__ = None

    ALL = 0
    BEARING = 1
    POINT_LOAD = 2
    POWER_LOAD = 3
    SHAFTHUB_CONNECTION = 4
    GEAR_MESH = 5
    UNCONNECTED = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ConnectedComponentType.__setattr__ = __enum_setattr
ConnectedComponentType.__delattr__ = __enum_delattr
