'''_1627.py

DatabaseWithSelectedItem
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')


__docformat__ = 'restructuredtext en'
__all__ = ('DatabaseWithSelectedItem',)


class DatabaseWithSelectedItem(_0.APIBase):
    '''DatabaseWithSelectedItem

    This is a mastapy class.
    '''

    TYPE = _DATABASE_WITH_SELECTED_ITEM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatabaseWithSelectedItem.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def selected_item_name(self) -> 'str':
        '''str: 'SelectedItemName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SelectedItemName

    @property
    def items(self) -> 'List[str]':
        '''List[str]: 'Items' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Items, str)
        return value

    def set_selected_item(self, item_name: 'str'):
        ''' 'SetSelectedItem' is the original name of this method.

        Args:
            item_name (str)
        '''

        item_name = str(item_name)
        self.wrapped.SetSelectedItem(item_name if item_name else '')
