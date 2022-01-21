'''_591.py

HobEdgeTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HOB_EDGE_TYPES = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'HobEdgeTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('HobEdgeTypes',)


class HobEdgeTypes(Enum):
    '''HobEdgeTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HOB_EDGE_TYPES

    __hash__ = None

    ARC = 0
    CATMULLROM_SPLINE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HobEdgeTypes.__setattr__ = __enum_setattr
HobEdgeTypes.__delattr__ = __enum_delattr
