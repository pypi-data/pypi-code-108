'''_1714.py

Orientations
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ORIENTATIONS = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'Orientations')


__docformat__ = 'restructuredtext en'
__all__ = ('Orientations',)


class Orientations(Enum):
    '''Orientations

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ORIENTATIONS

    __hash__ = None

    FLIPPED = 0
    DEFAULT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Orientations.__setattr__ = __enum_setattr
Orientations.__delattr__ = __enum_delattr
