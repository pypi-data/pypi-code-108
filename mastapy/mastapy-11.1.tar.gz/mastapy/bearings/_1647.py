'''_1647.py

RatingLife
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RATING_LIFE = python_net_import('SMT.MastaAPI.Bearings', 'RatingLife')


__docformat__ = 'restructuredtext en'
__all__ = ('RatingLife',)


class RatingLife(Enum):
    '''RatingLife

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RATING_LIFE

    __hash__ = None

    _10 = 0
    _5 = 1
    _4 = 2
    _3 = 3
    _2 = 4
    _1 = 5
    _08 = 6
    _06 = 7
    _04 = 8
    _02 = 9
    _01 = 10
    _008 = 11
    _006 = 12
    _005 = 13


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RatingLife.__setattr__ = __enum_setattr
RatingLife.__delattr__ = __enum_delattr
