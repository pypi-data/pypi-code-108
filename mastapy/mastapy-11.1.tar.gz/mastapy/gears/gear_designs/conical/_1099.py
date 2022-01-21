'''_1099.py

ConicalFlanks
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONICAL_FLANKS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'ConicalFlanks')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalFlanks',)


class ConicalFlanks(Enum):
    '''ConicalFlanks

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONICAL_FLANKS

    __hash__ = None

    CONCAVE = 0
    CONVEX = 1
    WORST = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ConicalFlanks.__setattr__ = __enum_setattr
ConicalFlanks.__delattr__ = __enum_delattr
