'''_7.py

CastingFactorCondition
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CASTING_FACTOR_CONDITION = python_net_import('SMT.MastaAPI.Shafts', 'CastingFactorCondition')


__docformat__ = 'restructuredtext en'
__all__ = ('CastingFactorCondition',)


class CastingFactorCondition(Enum):
    '''CastingFactorCondition

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CASTING_FACTOR_CONDITION

    __hash__ = None

    CASTINGS_NOT_SUBJECT_TO_NONDESTRUCTIVE_TESTING = 0
    CASTINGS_SUBJECT_TO_NONDESTRUCTIVE_TESTING = 1
    HIGH_QUALITY_CAST_COMPONENTS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CastingFactorCondition.__setattr__ = __enum_setattr
CastingFactorCondition.__delattr__ = __enum_delattr
