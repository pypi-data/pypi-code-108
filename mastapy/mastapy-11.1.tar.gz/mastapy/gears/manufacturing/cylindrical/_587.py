'''_587.py

Flank
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FLANK = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'Flank')


__docformat__ = 'restructuredtext en'
__all__ = ('Flank',)


class Flank(Enum):
    '''Flank

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FLANK

    __hash__ = None

    LEFT_FLANK = 0
    RIGHT_FLANK = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Flank.__setattr__ = __enum_setattr
Flank.__delattr__ = __enum_delattr
