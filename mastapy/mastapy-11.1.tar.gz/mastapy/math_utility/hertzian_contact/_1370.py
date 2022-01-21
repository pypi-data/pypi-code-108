'''_1370.py

HertzianContactDeflectionCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HERTZIAN_CONTACT_DEFLECTION_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.MathUtility.HertzianContact', 'HertzianContactDeflectionCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('HertzianContactDeflectionCalculationMethod',)


class HertzianContactDeflectionCalculationMethod(Enum):
    '''HertzianContactDeflectionCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HERTZIAN_CONTACT_DEFLECTION_CALCULATION_METHOD

    __hash__ = None

    WEBER = 0
    SIMPLIFIED_WEBER = 1
    HOUPERT_VERSION_1 = 2
    HOUPERT_VERSION_2 = 3
    PALMGREN = 4
    MODIFIED_PALMGREN = 5
    LI = 6
    TRIPP = 7
    UMEZAWA = 8


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HertzianContactDeflectionCalculationMethod.__setattr__ = __enum_setattr
HertzianContactDeflectionCalculationMethod.__delattr__ = __enum_delattr
