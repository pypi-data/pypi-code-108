'''_1309.py

ExtrapolationOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_EXTRAPOLATION_OPTIONS = python_net_import('SMT.MastaAPI.MathUtility', 'ExtrapolationOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ExtrapolationOptions',)


class ExtrapolationOptions(Enum):
    '''ExtrapolationOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _EXTRAPOLATION_OPTIONS

    __hash__ = None

    FLAT = 0
    LINEAR = 1
    THROW_EXCEPTION = 2
    WRAP = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ExtrapolationOptions.__setattr__ = __enum_setattr
ExtrapolationOptions.__delattr__ = __enum_delattr
