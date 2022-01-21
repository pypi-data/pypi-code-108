'''_85.py

TransientSolverToleranceInputMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TRANSIENT_SOLVER_TOLERANCE_INPUT_METHOD = python_net_import('SMT.MastaAPI.NodalAnalysis', 'TransientSolverToleranceInputMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('TransientSolverToleranceInputMethod',)


class TransientSolverToleranceInputMethod(Enum):
    '''TransientSolverToleranceInputMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TRANSIENT_SOLVER_TOLERANCE_INPUT_METHOD

    __hash__ = None

    SIMPLE = 0
    ADVANCED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TransientSolverToleranceInputMethod.__setattr__ = __enum_setattr
TransientSolverToleranceInputMethod.__delattr__ = __enum_delattr
