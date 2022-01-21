'''_1630.py

BasicStaticLoadRatingCalculationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BASIC_STATIC_LOAD_RATING_CALCULATION_METHOD = python_net_import('SMT.MastaAPI.Bearings', 'BasicStaticLoadRatingCalculationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('BasicStaticLoadRatingCalculationMethod',)


class BasicStaticLoadRatingCalculationMethod(Enum):
    '''BasicStaticLoadRatingCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BASIC_STATIC_LOAD_RATING_CALCULATION_METHOD

    __hash__ = None

    ISO_76_STANDARD = 0
    ISO_76_SUPPLEMENT_2_HYBRID_BEARING_WITH_SILICON_NITRIDE_ELEMENTS = 1
    ISOTR_106571991_LARGE_RACE_GROOVE_RADII = 2
    USERSPECIFIED = 3
    ANSIABMA_92015_AND_ANSIABMA_112014 = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BasicStaticLoadRatingCalculationMethod.__setattr__ = __enum_setattr
BasicStaticLoadRatingCalculationMethod.__delattr__ = __enum_delattr
