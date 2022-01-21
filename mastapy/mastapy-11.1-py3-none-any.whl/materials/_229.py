'''_229.py

ISO76StaticSafetyFactorLimits
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ISO76_STATIC_SAFETY_FACTOR_LIMITS = python_net_import('SMT.MastaAPI.Materials', 'ISO76StaticSafetyFactorLimits')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO76StaticSafetyFactorLimits',)


class ISO76StaticSafetyFactorLimits(Enum):
    '''ISO76StaticSafetyFactorLimits

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ISO76_STATIC_SAFETY_FACTOR_LIMITS

    __hash__ = None

    QUIETRUNNING_APPLICATIONS_SMOOTHRUNNING_VIBRATIONFREE_HIGH_ROTATIONAL_ACCURACY = 0
    NORMALRUNNING_APPLICATIONS_SMOOTHRUNNING_VIBRATIONFREE_NORMAL_ROTATIONAL_ACCURACY = 1
    APPLICATIONS_SUBJECTED_TO_SHOCK_LOADS_PRONOUNCED_SHOCK_LOADS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ISO76StaticSafetyFactorLimits.__setattr__ = __enum_setattr
ISO76StaticSafetyFactorLimits.__delattr__ = __enum_delattr
