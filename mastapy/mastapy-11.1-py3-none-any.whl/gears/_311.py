'''_311.py

SafetyRequirementsAGMA
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SAFETY_REQUIREMENTS_AGMA = python_net_import('SMT.MastaAPI.Gears', 'SafetyRequirementsAGMA')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyRequirementsAGMA',)


class SafetyRequirementsAGMA(Enum):
    '''SafetyRequirementsAGMA

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SAFETY_REQUIREMENTS_AGMA

    __hash__ = None

    FEWER_THAN_1_FAILURE_IN_10_000 = 0
    FEWER_THAN_1_FAILURE_IN_1000 = 1
    FEWER_THAN_1_FAILURE_IN_100 = 2
    FEWER_THAN_1_FAILURE_IN_10 = 3
    FEWER_THAN_1_FAILURE_IN_2 = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SafetyRequirementsAGMA.__setattr__ = __enum_setattr
SafetyRequirementsAGMA.__delattr__ = __enum_delattr
