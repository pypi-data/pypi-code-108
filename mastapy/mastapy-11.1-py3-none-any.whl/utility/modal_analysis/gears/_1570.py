'''_1570.py

GearPositions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_GEAR_POSITIONS = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'GearPositions')


__docformat__ = 'restructuredtext en'
__all__ = ('GearPositions',)


class GearPositions(Enum):
    '''GearPositions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _GEAR_POSITIONS

    __hash__ = None

    UNSPECIFIED = 0
    PINION = 1
    WHEEL = 2
    SUN = 3
    PLANET = 4
    ANNULUS = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


GearPositions.__setattr__ = __enum_setattr
GearPositions.__delattr__ = __enum_delattr
