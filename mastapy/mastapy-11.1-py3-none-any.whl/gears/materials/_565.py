'''_565.py

RatingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RATING_METHODS = python_net_import('SMT.MastaAPI.Gears.Materials', 'RatingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('RatingMethods',)


class RatingMethods(Enum):
    '''RatingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RATING_METHODS

    __hash__ = None

    AGMA_2003C10 = 0
    GLEASON = 1
    ISO_103002014 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RatingMethods.__setattr__ = __enum_setattr
RatingMethods.__delattr__ = __enum_delattr
