'''_1005.py

GeometrySpecificationType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_GEOMETRY_SPECIFICATION_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'GeometrySpecificationType')


__docformat__ = 'restructuredtext en'
__all__ = ('GeometrySpecificationType',)


class GeometrySpecificationType(Enum):
    '''GeometrySpecificationType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _GEOMETRY_SPECIFICATION_TYPE

    __hash__ = None

    BASIC_RACK = 0
    PINION_TYPE_CUTTER = 1
    EXISTING_CUTTER_OBSOLETE = 2
    MANUFACTURING_CONFIGURATION = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


GeometrySpecificationType.__setattr__ = __enum_setattr
GeometrySpecificationType.__delattr__ = __enum_delattr
