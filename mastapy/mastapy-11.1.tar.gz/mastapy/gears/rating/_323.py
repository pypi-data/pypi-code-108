'''_323.py

FlankLoadingState
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FLANK_LOADING_STATE = python_net_import('SMT.MastaAPI.Gears.Rating', 'FlankLoadingState')


__docformat__ = 'restructuredtext en'
__all__ = ('FlankLoadingState',)


class FlankLoadingState(Enum):
    '''FlankLoadingState

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FLANK_LOADING_STATE

    __hash__ = None

    UNLOADED = 0
    DRIVING = 1
    DRIVEN = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FlankLoadingState.__setattr__ = __enum_setattr
FlankLoadingState.__delattr__ = __enum_delattr
