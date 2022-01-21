'''_394.py

ISO10300RatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ISO10300_RATING_METHOD = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300RatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300RatingMethod',)


class ISO10300RatingMethod(Enum):
    '''ISO10300RatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ISO10300_RATING_METHOD

    __hash__ = None

    METHOD_B1 = 0
    METHOD_B2 = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ISO10300RatingMethod.__setattr__ = __enum_setattr
ISO10300RatingMethod.__delattr__ = __enum_delattr
