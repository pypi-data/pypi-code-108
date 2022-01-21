'''_75.py

NodalMatrixRow
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NODAL_MATRIX_ROW = python_net_import('SMT.MastaAPI.NodalAnalysis', 'NodalMatrixRow')


__docformat__ = 'restructuredtext en'
__all__ = ('NodalMatrixRow',)


class NodalMatrixRow(_0.APIBase):
    '''NodalMatrixRow

    This is a mastapy class.
    '''

    TYPE = _NODAL_MATRIX_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodalMatrixRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def node_index(self) -> 'int':
        '''int: 'NodeIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NodeIndex

    @property
    def degree_of_freedom(self) -> 'int':
        '''int: 'DegreeOfFreedom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DegreeOfFreedom

    @property
    def comma_separated_values(self) -> 'str':
        '''str: 'CommaSeparatedValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CommaSeparatedValues

    @property
    def values(self) -> 'List[float]':
        '''List[float]: 'Values' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Values, float)
        return value
