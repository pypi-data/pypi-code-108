'''_1115.py

KlingelnbergFinishingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_FINISHING_METHODS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'KlingelnbergFinishingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergFinishingMethods',)


class KlingelnbergFinishingMethods(Enum):
    '''KlingelnbergFinishingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _KLINGELNBERG_FINISHING_METHODS

    __hash__ = None

    LAPPED = 0
    SOFTCUT = 1
    HPG = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


KlingelnbergFinishingMethods.__setattr__ = __enum_setattr
KlingelnbergFinishingMethods.__delattr__ = __enum_delattr
