'''_97.py

DenseStiffnessSolver
'''


from mastapy.nodal_analysis.system_solvers import _110
from mastapy._internal.python_net import python_net_import

_DENSE_STIFFNESS_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'DenseStiffnessSolver')


__docformat__ = 'restructuredtext en'
__all__ = ('DenseStiffnessSolver',)


class DenseStiffnessSolver(_110.Solver):
    '''DenseStiffnessSolver

    This is a mastapy class.
    '''

    TYPE = _DENSE_STIFFNESS_SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DenseStiffnessSolver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
