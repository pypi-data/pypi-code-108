'''_1720.py

BallBearingContactCalculation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BALL_BEARING_CONTACT_CALCULATION = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'BallBearingContactCalculation')


__docformat__ = 'restructuredtext en'
__all__ = ('BallBearingContactCalculation',)


class BallBearingContactCalculation(Enum):
    '''BallBearingContactCalculation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BALL_BEARING_CONTACT_CALCULATION

    __hash__ = None

    FULL = 0
    BREWE_AND_HAMROCK_1977 = 1
    HAMROCK_AND_BREWE_1983 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BallBearingContactCalculation.__setattr__ = __enum_setattr
BallBearingContactCalculation.__delattr__ = __enum_delattr
