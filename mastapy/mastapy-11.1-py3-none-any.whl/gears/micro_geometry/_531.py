'''_531.py

FlankSide
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FLANK_SIDE = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'FlankSide')


__docformat__ = 'restructuredtext en'
__all__ = ('FlankSide',)


class FlankSide(Enum):
    '''FlankSide

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FLANK_SIDE

    __hash__ = None

    LEFT_SIDE = 0
    RIGHT_SIDE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FlankSide.__setattr__ = __enum_setattr
FlankSide.__delattr__ = __enum_delattr
