'''_1007.py

HardnessProfileCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HARDNESS_PROFILE_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'HardnessProfileCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('HardnessProfileCalculationMethod',)


class HardnessProfileCalculationMethod(Enum):
    '''HardnessProfileCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HARDNESS_PROFILE_CALCULATION_METHOD

    __hash__ = None

    MACKALDENER = 0
    TOBE = 1
    LANG = 2
    THOMAS = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HardnessProfileCalculationMethod.__setattr__ = __enum_setattr
HardnessProfileCalculationMethod.__delattr__ = __enum_delattr
