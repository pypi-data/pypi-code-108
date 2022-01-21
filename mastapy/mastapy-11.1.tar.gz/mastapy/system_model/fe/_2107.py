'''_2107.py

BearingRacePosition
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_RACE_POSITION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'BearingRacePosition')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingRacePosition',)


class BearingRacePosition(Enum):
    '''BearingRacePosition

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_RACE_POSITION

    __hash__ = None

    INNER = 0
    OUTER = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingRacePosition.__setattr__ = __enum_setattr
BearingRacePosition.__delattr__ = __enum_delattr
