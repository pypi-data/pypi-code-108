'''_221.py

CylindricalGearRatingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_RATING_METHODS = python_net_import('SMT.MastaAPI.Materials', 'CylindricalGearRatingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearRatingMethods',)


class CylindricalGearRatingMethods(Enum):
    '''CylindricalGearRatingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CYLINDRICAL_GEAR_RATING_METHODS

    __hash__ = None

    STANDARD_WITHDRAWN = 0
    AGMA_2101D04 = 1
    ISO_63362019 = 2
    ISO_63362006 = 3
    ISO_63361996 = 4
    DIN_39901987 = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CylindricalGearRatingMethods.__setattr__ = __enum_setattr
CylindricalGearRatingMethods.__delattr__ = __enum_delattr
