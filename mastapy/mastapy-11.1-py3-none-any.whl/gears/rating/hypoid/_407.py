'''_407.py

HypoidRatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HYPOID_RATING_METHOD = python_net_import('SMT.MastaAPI.Gears.Rating.Hypoid', 'HypoidRatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidRatingMethod',)


class HypoidRatingMethod(Enum):
    '''HypoidRatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HYPOID_RATING_METHOD

    __hash__ = None

    GLEASON = 0
    ISO_103002014 = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HypoidRatingMethod.__setattr__ = __enum_setattr
HypoidRatingMethod.__delattr__ = __enum_delattr
