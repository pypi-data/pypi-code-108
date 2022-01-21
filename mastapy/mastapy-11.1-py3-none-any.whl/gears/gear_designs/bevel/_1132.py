'''_1132.py

EdgeRadiusType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_EDGE_RADIUS_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'EdgeRadiusType')


__docformat__ = 'restructuredtext en'
__all__ = ('EdgeRadiusType',)


class EdgeRadiusType(Enum):
    '''EdgeRadiusType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _EDGE_RADIUS_TYPE

    __hash__ = None

    USERSPECIFIED = 0
    CALCULATED_MAXIMUM = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


EdgeRadiusType.__setattr__ = __enum_setattr
EdgeRadiusType.__delattr__ = __enum_delattr
