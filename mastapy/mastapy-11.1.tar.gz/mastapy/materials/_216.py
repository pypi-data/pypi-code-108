'''_216.py

BearingLubricationCondition
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_LUBRICATION_CONDITION = python_net_import('SMT.MastaAPI.Materials', 'BearingLubricationCondition')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingLubricationCondition',)


class BearingLubricationCondition(Enum):
    '''BearingLubricationCondition

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_LUBRICATION_CONDITION

    __hash__ = None

    OIL_LEVEL_TAKEN_FROM_ASSEMBLY = 0
    OIL_SPLASH_LUBRICATION_BEARING_IN_OIL_MIST = 1
    OIL_SPLASH_LUBRICATION_OIL_LEVEL_TO_MIDDLE_OF_BEARING = 2
    OIL_SPLASH_LUBRICATION_OIL_LEVEL_TO_MIDDLE_OF_LOWEST_ELEMENT = 3
    OIL_CIRCULATING_LUBRICATION = 4
    GREASE_RUNIN_BEARING = 5
    GREASE_NEWLY_GREASED = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingLubricationCondition.__setattr__ = __enum_setattr
BearingLubricationCondition.__delattr__ = __enum_delattr
