'''_438.py

MicropittingRatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICROPITTING_RATING_METHOD = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'MicropittingRatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('MicropittingRatingMethod',)


class MicropittingRatingMethod(Enum):
    '''MicropittingRatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICROPITTING_RATING_METHOD

    __hash__ = None

    ISOTR_1514412010 = 0
    ISOTR_1514412014 = 1
    ISOTS_6336222018 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicropittingRatingMethod.__setattr__ = __enum_setattr
MicropittingRatingMethod.__delattr__ = __enum_delattr
