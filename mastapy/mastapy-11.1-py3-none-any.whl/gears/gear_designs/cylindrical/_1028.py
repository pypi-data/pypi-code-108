'''_1028.py

ShaperEdgeTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SHAPER_EDGE_TYPES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ShaperEdgeTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaperEdgeTypes',)


class ShaperEdgeTypes(Enum):
    '''ShaperEdgeTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SHAPER_EDGE_TYPES

    __hash__ = None

    SINGLE_CIRCLE = 0
    CATMULLROM_SPLINE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ShaperEdgeTypes.__setattr__ = __enum_setattr
ShaperEdgeTypes.__delattr__ = __enum_delattr
