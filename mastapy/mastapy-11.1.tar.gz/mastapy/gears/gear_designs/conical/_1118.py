'''_1118.py

TopremLetter
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TOPREM_LETTER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'TopremLetter')


__docformat__ = 'restructuredtext en'
__all__ = ('TopremLetter',)


class TopremLetter(Enum):
    '''TopremLetter

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TOPREM_LETTER

    __hash__ = None

    F = 0
    E = 1
    C = 2
    B = 3
    A = 4
    Z = 5
    W = 6
    M = 7
    FY = 8
    EY = 9
    CY = 10
    BY = 11
    AY = 12
    FH = 13
    EH = 14
    CH = 15
    BH = 16
    AH = 17
    ZH = 18
    WH = 19
    MH = 20
    FJ = 21
    EJ = 22
    CJ = 23
    BJ = 24
    AJ = 25
    ZJ = 26
    WJ = 27
    MJ = 28
    FK = 29
    EK = 30
    CK = 31
    BK = 32
    AK = 33
    ZK = 34
    WK = 35
    MK = 36


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TopremLetter.__setattr__ = __enum_setattr
TopremLetter.__delattr__ = __enum_delattr
