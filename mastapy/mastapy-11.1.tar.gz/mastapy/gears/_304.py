'''_304.py

MicropittingCoefficientOfFrictionCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICROPITTING_COEFFICIENT_OF_FRICTION_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.Gears', 'MicropittingCoefficientOfFrictionCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('MicropittingCoefficientOfFrictionCalculationMethod',)


class MicropittingCoefficientOfFrictionCalculationMethod(Enum):
    '''MicropittingCoefficientOfFrictionCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICROPITTING_COEFFICIENT_OF_FRICTION_CALCULATION_METHOD

    __hash__ = None

    CALCULATED_CONSTANT = 0
    VARIABLE_BENEDICT_AND_KELLEY = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicropittingCoefficientOfFrictionCalculationMethod.__setattr__ = __enum_setattr
MicropittingCoefficientOfFrictionCalculationMethod.__delattr__ = __enum_delattr
