'''_1061.py

DrawDefiningGearOrBoth
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DRAW_DEFINING_GEAR_OR_BOTH = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'DrawDefiningGearOrBoth')


__docformat__ = 'restructuredtext en'
__all__ = ('DrawDefiningGearOrBoth',)


class DrawDefiningGearOrBoth(Enum):
    '''DrawDefiningGearOrBoth

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DRAW_DEFINING_GEAR_OR_BOTH

    __hash__ = None

    DEFINING_GEAR = 0
    BOTH = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DrawDefiningGearOrBoth.__setattr__ = __enum_setattr
DrawDefiningGearOrBoth.__delattr__ = __enum_delattr
