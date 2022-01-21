'''_1319.py

ComplexMagnitudeMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COMPLEX_MAGNITUDE_METHOD = python_net_import('SMT.MastaAPI.MathUtility', 'ComplexMagnitudeMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ComplexMagnitudeMethod',)


class ComplexMagnitudeMethod(Enum):
    '''ComplexMagnitudeMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COMPLEX_MAGNITUDE_METHOD

    __hash__ = None

    PEAK_AMPLITUDE = 0
    PEAKTOPEAK_AMPLITUDE = 1
    RMS_AMPLITUDE = 2
    MAGNITUDE_OF_COMPLEX_MODULI = 3
    MAGNITUDE_OF_COMPLEX_VALUES = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ComplexMagnitudeMethod.__setattr__ = __enum_setattr
ComplexMagnitudeMethod.__delattr__ = __enum_delattr
