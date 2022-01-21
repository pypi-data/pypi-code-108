'''_1313.py

GenericMatrix
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GENERIC_MATRIX = python_net_import('SMT.MastaAPI.MathUtility', 'GenericMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('GenericMatrix',)


TElement = TypeVar('TElement', bound='object')
TMatrix = TypeVar('TMatrix', bound='GenericMatrix')


class GenericMatrix(_0.APIBase, Generic[TElement, TMatrix]):
    '''GenericMatrix

    This is a mastapy class.

    Generic Types:
        TElement
        TMatrix
    '''

    TYPE = _GENERIC_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GenericMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_rows(self) -> 'int':
        '''int: 'NumberOfRows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfRows

    @property
    def number_of_columns(self) -> 'int':
        '''int: 'NumberOfColumns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfColumns

    @property
    def number_of_entries(self) -> 'int':
        '''int: 'NumberOfEntries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfEntries

    @property
    def data(self) -> 'List[TElement]':
        '''List[TElement]: 'Data' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Data)
        return value
