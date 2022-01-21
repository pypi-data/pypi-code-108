'''_108.py

SingularValuesAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.nodal_analysis.system_solvers import _109
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SINGULAR_VALUES_ANALYSIS = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'SingularValuesAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SingularValuesAnalysis',)


class SingularValuesAnalysis(_0.APIBase):
    '''SingularValuesAnalysis

    This is a mastapy class.
    '''

    TYPE = _SINGULAR_VALUES_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingularValuesAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def stiffness_matrix_rank(self) -> 'int':
        '''int: 'StiffnessMatrixRank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessMatrixRank

    @property
    def condition_number(self) -> 'float':
        '''float: 'ConditionNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConditionNumber

    @property
    def stiffness_matrix_degrees_of_freedom(self) -> 'int':
        '''int: 'StiffnessMatrixDegreesOfFreedom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessMatrixDegreesOfFreedom

    @property
    def smallest_singular_vectors(self) -> 'List[_109.SingularVectorAnalysis]':
        '''List[SingularVectorAnalysis]: 'SmallestSingularVectors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SmallestSingularVectors, constructor.new(_109.SingularVectorAnalysis))
        return value

    @property
    def largest_singular_vectors(self) -> 'List[_109.SingularVectorAnalysis]':
        '''List[SingularVectorAnalysis]: 'LargestSingularVectors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LargestSingularVectors, constructor.new(_109.SingularVectorAnalysis))
        return value
