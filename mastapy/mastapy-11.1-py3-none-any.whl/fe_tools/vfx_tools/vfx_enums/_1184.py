'''_1184.py

ProSolveSolverType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PRO_SOLVE_SOLVER_TYPE = python_net_import('SMT.MastaAPI.FETools.VfxTools.VfxEnums', 'ProSolveSolverType')


__docformat__ = 'restructuredtext en'
__all__ = ('ProSolveSolverType',)


class ProSolveSolverType(Enum):
    '''ProSolveSolverType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PRO_SOLVE_SOLVER_TYPE

    __hash__ = None

    LEFTLOOKING = 4
    SERIAL_MULTIFRONTAL = 5
    PARALLEL_MULTIFRONTAL = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ProSolveSolverType.__setattr__ = __enum_setattr
ProSolveSolverType.__delattr__ = __enum_delattr
