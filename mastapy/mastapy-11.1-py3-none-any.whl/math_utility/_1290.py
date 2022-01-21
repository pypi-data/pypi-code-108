'''_1290.py

Axis
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AXIS = python_net_import('SMT.MastaAPI.MathUtility', 'Axis')


__docformat__ = 'restructuredtext en'
__all__ = ('Axis',)


class Axis(Enum):
    '''Axis

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AXIS

    __hash__ = None

    X = 0
    Y = 1
    Z = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Axis.__setattr__ = __enum_setattr
Axis.__delattr__ = __enum_delattr
