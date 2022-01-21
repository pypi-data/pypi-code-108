'''_1581.py

NamedTuple3
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_TUPLE_3 = python_net_import('SMT.MastaAPI.Utility.Generics', 'NamedTuple3')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedTuple3',)


T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')


class NamedTuple3(_0.APIBase, Generic[T1, T2, T3]):
    '''NamedTuple3

    This is a mastapy class.

    Generic Types:
        T1
        T2
        T3
    '''

    TYPE = _NAMED_TUPLE_3

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedTuple3.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def item_1(self) -> 'T1':
        '''T1: 'Item1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Item1

    @property
    def item_2(self) -> 'T2':
        '''T2: 'Item2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Item2

    @property
    def item_3(self) -> 'T3':
        '''T3: 'Item3' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Item3

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
