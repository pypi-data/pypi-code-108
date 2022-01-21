'''_316.py

WormAddendumFactor
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_WORM_ADDENDUM_FACTOR = python_net_import('SMT.MastaAPI.Gears', 'WormAddendumFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('WormAddendumFactor',)


class WormAddendumFactor(Enum):
    '''WormAddendumFactor

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _WORM_ADDENDUM_FACTOR

    __hash__ = None

    NORMAL = 0
    STUB = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


WormAddendumFactor.__setattr__ = __enum_setattr
WormAddendumFactor.__delattr__ = __enum_delattr
