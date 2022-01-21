'''_109.py

SingularVectorAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.nodal_analysis.system_solvers import _107
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SINGULAR_VECTOR_ANALYSIS = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'SingularVectorAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SingularVectorAnalysis',)


class SingularVectorAnalysis(_0.APIBase):
    '''SingularVectorAnalysis

    This is a mastapy class.
    '''

    TYPE = _SINGULAR_VECTOR_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingularVectorAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def singular_value(self) -> 'float':
        '''float: 'SingularValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingularValue

    @property
    def largest_singular_vector_components(self) -> 'List[_107.SingularDegreeOfFreedomAnalysis]':
        '''List[SingularDegreeOfFreedomAnalysis]: 'LargestSingularVectorComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LargestSingularVectorComponents, constructor.new(_107.SingularDegreeOfFreedomAnalysis))
        return value
