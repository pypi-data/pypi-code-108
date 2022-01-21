'''_1717.py

RaceAxialMountingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RACE_AXIAL_MOUNTING_TYPE = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'RaceAxialMountingType')


__docformat__ = 'restructuredtext en'
__all__ = ('RaceAxialMountingType',)


class RaceAxialMountingType(Enum):
    '''RaceAxialMountingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RACE_AXIAL_MOUNTING_TYPE

    __hash__ = None

    BOTH = 0
    LEFT = 1
    RIGHT = 2
    NONE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RaceAxialMountingType.__setattr__ = __enum_setattr
RaceAxialMountingType.__delattr__ = __enum_delattr
