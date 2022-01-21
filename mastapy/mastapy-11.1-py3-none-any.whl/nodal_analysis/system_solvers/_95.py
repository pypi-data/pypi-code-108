'''_95.py

BackwardEulerAccelerationStepHalvingTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _105
from mastapy._internal.python_net import python_net_import

_BACKWARD_EULER_ACCELERATION_STEP_HALVING_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'BackwardEulerAccelerationStepHalvingTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('BackwardEulerAccelerationStepHalvingTransientSolver',)


class BackwardEulerAccelerationStepHalvingTransientSolver(_105.SimpleAccelerationBasedStepHalvingTransientSolver):
    '''BackwardEulerAccelerationStepHalvingTransientSolver

    This is a mastapy class.
    '''

    TYPE = _BACKWARD_EULER_ACCELERATION_STEP_HALVING_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BackwardEulerAccelerationStepHalvingTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
