'''_1815.py

PowerRatingF1EstimationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_POWER_RATING_F1_ESTIMATION_METHOD = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'PowerRatingF1EstimationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerRatingF1EstimationMethod',)


class PowerRatingF1EstimationMethod(Enum):
    '''PowerRatingF1EstimationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _POWER_RATING_F1_ESTIMATION_METHOD

    __hash__ = None

    ISOTR_141792001 = 0
    USER_SPECIFIED = 1
    ONEDIMENSIONAL_LOOKUP_TABLE = 2
    TWODIMENSIONAL_LOOKUP_TABLE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PowerRatingF1EstimationMethod.__setattr__ = __enum_setattr
PowerRatingF1EstimationMethod.__delattr__ = __enum_delattr
