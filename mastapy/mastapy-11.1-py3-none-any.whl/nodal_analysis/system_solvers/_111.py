'''_111.py

StepHalvingTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _99
from mastapy._internal.python_net import python_net_import

_STEP_HALVING_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'StepHalvingTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('StepHalvingTransientSolver',)


class StepHalvingTransientSolver(_99.InternalTransientSolver):
    '''StepHalvingTransientSolver

    This is a mastapy class.
    '''

    TYPE = _STEP_HALVING_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StepHalvingTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
