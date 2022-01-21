'''_114.py

WilsonThetaTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _111
from mastapy._internal.python_net import python_net_import

_WILSON_THETA_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'WilsonThetaTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('WilsonThetaTransientSolver',)


class WilsonThetaTransientSolver(_111.StepHalvingTransientSolver):
    '''WilsonThetaTransientSolver

    This is a mastapy class.
    '''

    TYPE = _WILSON_THETA_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WilsonThetaTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
