'''_1293.py

ComplexPartDisplayOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COMPLEX_PART_DISPLAY_OPTION = python_net_import('SMT.MastaAPI.MathUtility', 'ComplexPartDisplayOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ComplexPartDisplayOption',)


class ComplexPartDisplayOption(Enum):
    '''ComplexPartDisplayOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COMPLEX_PART_DISPLAY_OPTION

    __hash__ = None

    AMPLITUDE = 0
    PEAKTOPEAK_AMPLITUDE = 1
    RMS_AMPLITUDE = 2
    PHASE = 3
    REAL = 4
    IMAGINARY = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ComplexPartDisplayOption.__setattr__ = __enum_setattr
ComplexPartDisplayOption.__delattr__ = __enum_delattr
