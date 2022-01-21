'''_1583.py

NamedTuple5
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_TUPLE_5 = python_net_import('SMT.MastaAPI.Utility.Generics', 'NamedTuple5')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedTuple5',)


T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')


class NamedTuple5(_0.APIBase, Generic[T1, T2, T3, T4, T5]):
    '''NamedTuple5

    This is a mastapy class.

    Generic Types:
        T1
        T2
        T3
        T4
        T5
    '''

    TYPE = _NAMED_TUPLE_5

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedTuple5.TYPE'):
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
    def item_4(self) -> 'T4':
        '''T4: 'Item4' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Item4

    @property
    def item_5(self) -> 'T5':
        '''T5: 'Item5' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Item5

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
