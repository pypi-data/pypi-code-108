'''_84.py

TransientSolverStatus
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TRANSIENT_SOLVER_STATUS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'TransientSolverStatus')


__docformat__ = 'restructuredtext en'
__all__ = ('TransientSolverStatus',)


class TransientSolverStatus(Enum):
    '''TransientSolverStatus

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TRANSIENT_SOLVER_STATUS

    __hash__ = None

    NONE = 0
    PREPARED_FOR_ANALYSIS = 1
    ANALYSIS_RUNNING = 2
    END_TIME_REACHED = 3
    MAXIMUM_TIME_STEPS_REACHED = 4
    ANALYSIS_ABORTED = 5
    ERROR_OCCURRED = 6
    END_MINOR_STEP_REACHED = 7


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TransientSolverStatus.__setattr__ = __enum_setattr
TransientSolverStatus.__delattr__ = __enum_delattr
