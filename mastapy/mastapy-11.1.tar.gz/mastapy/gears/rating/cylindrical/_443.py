'''_443.py

ScuffingIntegralTemperatureRatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SCUFFING_INTEGRAL_TEMPERATURE_RATING_METHOD = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'ScuffingIntegralTemperatureRatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ScuffingIntegralTemperatureRatingMethod',)


class ScuffingIntegralTemperatureRatingMethod(Enum):
    '''ScuffingIntegralTemperatureRatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SCUFFING_INTEGRAL_TEMPERATURE_RATING_METHOD

    __hash__ = None

    ISOTR_1398922000 = 0
    ISOTS_6336212017 = 1
    DIN_399041987 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ScuffingIntegralTemperatureRatingMethod.__setattr__ = __enum_setattr
ScuffingIntegralTemperatureRatingMethod.__delattr__ = __enum_delattr
