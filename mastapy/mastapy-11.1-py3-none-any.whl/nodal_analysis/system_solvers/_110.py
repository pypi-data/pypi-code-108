'''_110.py

Solver
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SOLVER = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'Solver')


__docformat__ = 'restructuredtext en'
__all__ = ('Solver',)


class Solver(_0.APIBase):
    '''Solver

    This is a mastapy class.
    '''

    TYPE = _SOLVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Solver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_nodes(self) -> 'int':
        '''int: 'NumberOfNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfNodes

    @property
    def total_number_of_degrees_of_freedom(self) -> 'int':
        '''int: 'TotalNumberOfDegreesOfFreedom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalNumberOfDegreesOfFreedom
