'''_1652.py

RollingBearingRaceType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROLLING_BEARING_RACE_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'RollingBearingRaceType')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearingRaceType',)


class RollingBearingRaceType(Enum):
    '''RollingBearingRaceType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROLLING_BEARING_RACE_TYPE

    __hash__ = None

    NONE = 0
    DRAWN = 1
    MACHINED = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RollingBearingRaceType.__setattr__ = __enum_setattr
RollingBearingRaceType.__delattr__ = __enum_delattr
