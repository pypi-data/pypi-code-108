'''_289.py

CylindricalFlanks
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_FLANKS = python_net_import('SMT.MastaAPI.Gears', 'CylindricalFlanks')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalFlanks',)


class CylindricalFlanks(Enum):
    '''CylindricalFlanks

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CYLINDRICAL_FLANKS

    __hash__ = None

    LEFT = 0
    RIGHT = 1
    WORST = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CylindricalFlanks.__setattr__ = __enum_setattr
CylindricalFlanks.__delattr__ = __enum_delattr
