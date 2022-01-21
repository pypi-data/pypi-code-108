'''_441.py

RatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RATING_METHOD = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'RatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('RatingMethod',)


class RatingMethod(Enum):
    '''RatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RATING_METHOD

    __hash__ = None

    METHOD_B = 0
    METHOD_C = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RatingMethod.__setattr__ = __enum_setattr
RatingMethod.__delattr__ = __enum_delattr
