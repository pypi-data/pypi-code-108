'''_285.py

CoefficientOfFrictionCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COEFFICIENT_OF_FRICTION_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.Gears', 'CoefficientOfFrictionCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('CoefficientOfFrictionCalculationMethod',)


class CoefficientOfFrictionCalculationMethod(Enum):
    '''CoefficientOfFrictionCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COEFFICIENT_OF_FRICTION_CALCULATION_METHOD

    __hash__ = None

    ISOTR_1417912001 = 0
    ISOTR_1417912001_WITH_SURFACE_ROUGHNESS_PARAMETER = 1
    ISOTR_1417922001 = 2
    ISOTR_1417922001_MARTINS_ET_AL = 3
    DROZDOV_AND_GAVRIKOV = 4
    ODONOGHUE_AND_CAMERON = 5
    MISHARIN = 6
    ISO_TC60 = 7
    BENEDICT_AND_KELLEY = 8
    USER_SPECIFIED = 9


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CoefficientOfFrictionCalculationMethod.__setattr__ = __enum_setattr
CoefficientOfFrictionCalculationMethod.__delattr__ = __enum_delattr
