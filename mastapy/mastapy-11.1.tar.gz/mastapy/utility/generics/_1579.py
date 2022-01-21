'''_1579.py

NamedTuple1
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_TUPLE_1 = python_net_import('SMT.MastaAPI.Utility.Generics', 'NamedTuple1')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedTuple1',)


T1 = TypeVar('T1')


class NamedTuple1(_0.APIBase, Generic[T1]):
    '''NamedTuple1

    This is a mastapy class.

    Generic Types:
        T1
    '''

    TYPE = _NAMED_TUPLE_1

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedTuple1.TYPE'):
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
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
