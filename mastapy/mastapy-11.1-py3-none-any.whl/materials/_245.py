'''_245.py

PressureViscosityCoefficientMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PRESSURE_VISCOSITY_COEFFICIENT_METHOD = python_net_import('SMT.MastaAPI.Materials', 'PressureViscosityCoefficientMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('PressureViscosityCoefficientMethod',)


class PressureViscosityCoefficientMethod(Enum):
    '''PressureViscosityCoefficientMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PRESSURE_VISCOSITY_COEFFICIENT_METHOD

    __hash__ = None

    TEMPERATURE_INDEPENDENT_VALUE = 0
    TEMPERATURE_AND_VALUE_AT_TEMPERATURE_SPECIFIED = 1
    SPECIFY_K_AND_S = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PressureViscosityCoefficientMethod.__setattr__ = __enum_setattr
PressureViscosityCoefficientMethod.__delattr__ = __enum_delattr
