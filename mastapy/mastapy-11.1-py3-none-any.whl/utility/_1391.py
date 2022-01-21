'''_1391.py

RoundingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROUNDING_METHODS = python_net_import('SMT.MastaAPI.Utility', 'RoundingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('RoundingMethods',)


class RoundingMethods(Enum):
    '''RoundingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROUNDING_METHODS

    __hash__ = None

    AUTO = 0
    SIGNIFICANT_FIGURES = 1
    DECIMAL_PLACES = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RoundingMethods.__setattr__ = __enum_setattr
RoundingMethods.__delattr__ = __enum_delattr
