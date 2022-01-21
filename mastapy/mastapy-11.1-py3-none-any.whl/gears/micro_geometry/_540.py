'''_540.py

ParabolicRootReliefStartsTangentToMainProfileRelief
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PARABOLIC_ROOT_RELIEF_STARTS_TANGENT_TO_MAIN_PROFILE_RELIEF = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'ParabolicRootReliefStartsTangentToMainProfileRelief')


__docformat__ = 'restructuredtext en'
__all__ = ('ParabolicRootReliefStartsTangentToMainProfileRelief',)


class ParabolicRootReliefStartsTangentToMainProfileRelief(Enum):
    '''ParabolicRootReliefStartsTangentToMainProfileRelief

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PARABOLIC_ROOT_RELIEF_STARTS_TANGENT_TO_MAIN_PROFILE_RELIEF

    __hash__ = None

    NO = 0
    YES = 1
    ONLY_WHEN_NONZERO_PARABOLIC_ROOT_RELIEF = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ParabolicRootReliefStartsTangentToMainProfileRelief.__setattr__ = __enum_setattr
ParabolicRootReliefStartsTangentToMainProfileRelief.__delattr__ = __enum_delattr
