'''_157.py

FEEntityGroup
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_ENTITY_GROUP = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEEntityGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('FEEntityGroup',)


T = TypeVar('T')


class FEEntityGroup(_0.APIBase, Generic[T]):
    '''FEEntityGroup

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _FE_ENTITY_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEEntityGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def number_of_items(self) -> 'int':
        '''int: 'NumberOfItems' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfItems
