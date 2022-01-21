'''_106.py

SimpleVelocityBasedStepHalvingTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _111
from mastapy._internal.python_net import python_net_import

_SIMPLE_VELOCITY_BASED_STEP_HALVING_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'SimpleVelocityBasedStepHalvingTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('SimpleVelocityBasedStepHalvingTransientSolver',)


class SimpleVelocityBasedStepHalvingTransientSolver(_111.StepHalvingTransientSolver):
    '''SimpleVelocityBasedStepHalvingTransientSolver

    This is a mastapy class.
    '''

    TYPE = _SIMPLE_VELOCITY_BASED_STEP_HALVING_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SimpleVelocityBasedStepHalvingTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
