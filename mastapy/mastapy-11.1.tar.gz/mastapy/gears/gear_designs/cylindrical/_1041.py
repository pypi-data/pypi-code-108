'''_1041.py

TypeOfMechanismHousing
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TYPE_OF_MECHANISM_HOUSING = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'TypeOfMechanismHousing')


__docformat__ = 'restructuredtext en'
__all__ = ('TypeOfMechanismHousing',)


class TypeOfMechanismHousing(Enum):
    '''TypeOfMechanismHousing

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TYPE_OF_MECHANISM_HOUSING

    __hash__ = None

    OPEN_WITH_UNIMPEDED_ENTRY_OF_AIR = 0
    PARTIALLY_OPEN_HOUSING_SPECIFY_A_PERCENTAGE = 1
    CLOSED_HOUSING = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TypeOfMechanismHousing.__setattr__ = __enum_setattr
TypeOfMechanismHousing.__delattr__ = __enum_delattr
