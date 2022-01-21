'''_1302.py

DegreesOfFreedom
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DEGREES_OF_FREEDOM = python_net_import('SMT.MastaAPI.MathUtility', 'DegreesOfFreedom')


__docformat__ = 'restructuredtext en'
__all__ = ('DegreesOfFreedom',)


class DegreesOfFreedom(Enum):
    '''DegreesOfFreedom

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DEGREES_OF_FREEDOM

    __hash__ = None

    X = 0
    Y = 1
    Z = 2
    ΘX = 3
    ΘY = 4
    ΘZ = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DegreesOfFreedom.__setattr__ = __enum_setattr
DegreesOfFreedom.__delattr__ = __enum_delattr
