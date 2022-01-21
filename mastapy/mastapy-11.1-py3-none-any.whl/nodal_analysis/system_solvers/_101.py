'''_101.py

LobattoIIICTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _111
from mastapy._internal.python_net import python_net_import

_LOBATTO_IIIC_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'LobattoIIICTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('LobattoIIICTransientSolver',)


class LobattoIIICTransientSolver(_111.StepHalvingTransientSolver):
    '''LobattoIIICTransientSolver

    This is a mastapy class.
    '''

    TYPE = _LOBATTO_IIIC_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LobattoIIICTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
