'''_77.py

RatingTypeForShaftReliability
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RATING_TYPE_FOR_SHAFT_RELIABILITY = python_net_import('SMT.MastaAPI.NodalAnalysis', 'RatingTypeForShaftReliability')


__docformat__ = 'restructuredtext en'
__all__ = ('RatingTypeForShaftReliability',)


class RatingTypeForShaftReliability(Enum):
    '''RatingTypeForShaftReliability

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RATING_TYPE_FOR_SHAFT_RELIABILITY

    __hash__ = None

    FATIGUE_FOR_FINITE_LIFE = 0
    FATIGUE_FOR_INFINITE_LIFE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RatingTypeForShaftReliability.__setattr__ = __enum_setattr
RatingTypeForShaftReliability.__delattr__ = __enum_delattr
