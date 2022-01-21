'''_74.py

NodalMatrix
'''


from typing import List

from mastapy.nodal_analysis import _75, _44
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_NODAL_MATRIX = python_net_import('SMT.MastaAPI.NodalAnalysis', 'NodalMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('NodalMatrix',)


class NodalMatrix(_44.AbstractNodalMatrix):
    '''NodalMatrix

    This is a mastapy class.
    '''

    TYPE = _NODAL_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodalMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rows(self) -> 'List[_75.NodalMatrixRow]':
        '''List[NodalMatrixRow]: 'Rows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Rows, constructor.new(_75.NodalMatrixRow))
        return value
