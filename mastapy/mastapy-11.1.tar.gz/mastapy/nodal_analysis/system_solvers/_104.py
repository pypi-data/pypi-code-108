'''_104.py

SemiImplicitTransientSolver
'''


from mastapy.nodal_analysis.system_solvers import _99
from mastapy._internal.python_net import python_net_import

_SEMI_IMPLICIT_TRANSIENT_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'SemiImplicitTransientSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('SemiImplicitTransientSolver',)


class SemiImplicitTransientSolver(_99.InternalTransientSolver):
    '''SemiImplicitTransientSolver

    This is a mastapy class.
    '''

    TYPE = _SEMI_IMPLICIT_TRANSIENT_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SemiImplicitTransientSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
