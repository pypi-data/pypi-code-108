'''_317.py

WormType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_WORM_TYPE = python_net_import('SMT.MastaAPI.Gears', 'WormType')


__docformat__ = 'restructuredtext en'
__all__ = ('WormType',)


class WormType(Enum):
    '''WormType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _WORM_TYPE

    __hash__ = None

    ZA = 0
    ZN = 1
    ZI = 2
    ZK = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


WormType.__setattr__ = __enum_setattr
WormType.__delattr__ = __enum_delattr
