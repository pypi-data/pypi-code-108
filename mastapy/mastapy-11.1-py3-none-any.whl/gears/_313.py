'''_313.py

SpiralBevelRootLineTilt
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_ROOT_LINE_TILT = python_net_import('SMT.MastaAPI.Gears', 'SpiralBevelRootLineTilt')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelRootLineTilt',)


class SpiralBevelRootLineTilt(Enum):
    '''SpiralBevelRootLineTilt

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SPIRAL_BEVEL_ROOT_LINE_TILT

    __hash__ = None

    ABOUT_MEAN_POINT = 0
    ABOUT_LARGE_END = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SpiralBevelRootLineTilt.__setattr__ = __enum_setattr
SpiralBevelRootLineTilt.__delattr__ = __enum_delattr
