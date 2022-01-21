'''_103.py

NewmarkTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _106
from mastapy._internal.python_net import python_net_import

_NEWMARK_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'NewmarkTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('NewmarkTransientSolver',)


class NewmarkTransientSolver(_106.SimpleVelocityBasedStepHalvingTransientSolver):
    '''NewmarkTransientSolver

    This is a mastapy class.
    '''

    TYPE = _NEWMARK_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NewmarkTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
