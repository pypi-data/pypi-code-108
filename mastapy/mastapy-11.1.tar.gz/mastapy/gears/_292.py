'''_292.py

GearFlanks
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_GEAR_FLANKS = python_net_import('SMT.MastaAPI.Gears', 'GearFlanks')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFlanks',)


class GearFlanks(Enum):
    '''GearFlanks

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _GEAR_FLANKS

    __hash__ = None

    FLANK_A = 0
    FLANK_B = 1
    WORST = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


GearFlanks.__setattr__ = __enum_setattr
GearFlanks.__delattr__ = __enum_delattr
