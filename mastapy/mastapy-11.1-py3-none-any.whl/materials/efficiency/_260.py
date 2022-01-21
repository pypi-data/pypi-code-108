'''_260.py

BearingEfficiencyRatingMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_EFFICIENCY_RATING_METHOD = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'BearingEfficiencyRatingMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingEfficiencyRatingMethod',)


class BearingEfficiencyRatingMethod(Enum):
    '''BearingEfficiencyRatingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_EFFICIENCY_RATING_METHOD

    __hash__ = None

    ISOTR_1417912001 = 0
    ISOTR_1417922001 = 1
    SKF_LOSS_MODEL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingEfficiencyRatingMethod.__setattr__ = __enum_setattr
BearingEfficiencyRatingMethod.__delattr__ = __enum_delattr
