'''_1629.py

BasicDynamicLoadRatingCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BASIC_DYNAMIC_LOAD_RATING_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.Bearings', 'BasicDynamicLoadRatingCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('BasicDynamicLoadRatingCalculationMethod',)


class BasicDynamicLoadRatingCalculationMethod(Enum):
    '''BasicDynamicLoadRatingCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BASIC_DYNAMIC_LOAD_RATING_CALCULATION_METHOD

    __hash__ = None

    ISO_2812007_STANDARD = 0
    ISO_281_A52011_HYBRID_BEARING_WITH_SILICON_NITRIDE_ELEMENTS = 1
    ISOTR_128112008E_USING_ACTUAL_BEARING_INTERNAL_GEOMETRY = 2
    USERSPECIFIED = 3
    ANSIABMA_92015_AND_ANSIABMA_112014 = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BasicDynamicLoadRatingCalculationMethod.__setattr__ = __enum_setattr
BasicDynamicLoadRatingCalculationMethod.__delattr__ = __enum_delattr
