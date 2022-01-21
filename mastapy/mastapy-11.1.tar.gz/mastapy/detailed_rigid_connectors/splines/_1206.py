'''_1206.py

SAEFatigueLifeFactorTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SAE_FATIGUE_LIFE_FACTOR_TYPES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'SAEFatigueLifeFactorTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('SAEFatigueLifeFactorTypes',)


class SAEFatigueLifeFactorTypes(Enum):
    '''SAEFatigueLifeFactorTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SAE_FATIGUE_LIFE_FACTOR_TYPES

    __hash__ = None

    UNIDIRECTIONAL = 0
    FULLY_REVERSED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SAEFatigueLifeFactorTypes.__setattr__ = __enum_setattr
SAEFatigueLifeFactorTypes.__delattr__ = __enum_delattr
