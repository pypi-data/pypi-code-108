'''_1596.py

NamedDatabase
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy.utility.databases import _1597, _1599, _1598
from mastapy._internal.python_net import python_net_import

_NAMED_DATABASE = python_net_import('SMT.MastaAPI.Utility.Databases', 'NamedDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedDatabase',)


TValue = TypeVar('TValue', bound='_1597.NamedDatabaseItem')


class NamedDatabase(_1599.SQLDatabase['_1598.NamedKey', 'TValue'], Generic[TValue]):
    '''NamedDatabase

    This is a mastapy class.

    Generic Types:
        TValue
    '''

    TYPE = _NAMED_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def create(self, name: 'str') -> 'TValue':
        ''' 'Create' is the original name of this method.

        Args:
            name (str)

        Returns:
            TValue
        '''

        name = str(name)
        method_result = self.wrapped.Create(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_value(self, name: 'str') -> 'TValue':
        ''' 'GetValue' is the original name of this method.

        Args:
            name (str)

        Returns:
            TValue
        '''

        name = str(name)
        method_result = self.wrapped.GetValue(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def rename(self, item: '_1597.NamedDatabaseItem', new_name: 'str') -> 'bool':
        ''' 'Rename' is the original name of this method.

        Args:
            item (mastapy.utility.databases.NamedDatabaseItem)
            new_name (str)

        Returns:
            bool
        '''

        new_name = str(new_name)
        method_result = self.wrapped.Rename(item.wrapped if item else None, new_name if new_name else '')
        return method_result

    def duplicate(self, new_name: 'str', item: '_1597.NamedDatabaseItem') -> '_1597.NamedDatabaseItem':
        ''' 'Duplicate' is the original name of this method.

        Args:
            new_name (str)
            item (mastapy.utility.databases.NamedDatabaseItem)

        Returns:
            mastapy.utility.databases.NamedDatabaseItem
        '''

        new_name = str(new_name)
        method_result = self.wrapped.Duplicate(new_name if new_name else '', item.wrapped if item else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
