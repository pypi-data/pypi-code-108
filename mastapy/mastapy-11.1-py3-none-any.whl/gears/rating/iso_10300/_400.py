'''_400.py

MountingConditionsOfPinionAndWheel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MOUNTING_CONDITIONS_OF_PINION_AND_WHEEL = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'MountingConditionsOfPinionAndWheel')


__docformat__ = 'restructuredtext en'
__all__ = ('MountingConditionsOfPinionAndWheel',)


class MountingConditionsOfPinionAndWheel(Enum):
    '''MountingConditionsOfPinionAndWheel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MOUNTING_CONDITIONS_OF_PINION_AND_WHEEL

    __hash__ = None

    NEITHER_MEMBER_CANTILEVER_MOUNTED = 0
    ONE_MEMBER_CANTILEVER_MOUNTED = 1
    BOTH_MEMBER_CANTILEVER_MOUNTED = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MountingConditionsOfPinionAndWheel.__setattr__ = __enum_setattr
MountingConditionsOfPinionAndWheel.__delattr__ = __enum_delattr
