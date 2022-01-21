'''_1725.py

FrictionModelForGyroscopicMoment
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FRICTION_MODEL_FOR_GYROSCOPIC_MOMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'FrictionModelForGyroscopicMoment')


__docformat__ = 'restructuredtext en'
__all__ = ('FrictionModelForGyroscopicMoment',)


class FrictionModelForGyroscopicMoment(Enum):
    '''FrictionModelForGyroscopicMoment

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FRICTION_MODEL_FOR_GYROSCOPIC_MOMENT

    __hash__ = None

    OUTER_RACEWAY_CONTROL = 0
    INNER_RACEWAY_CONTROL = 1
    HYBRID_MODEL = 2
    ADAPTIVE_RACEWAY_CONTROL = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FrictionModelForGyroscopicMoment.__setattr__ = __enum_setattr
FrictionModelForGyroscopicMoment.__delattr__ = __enum_delattr
