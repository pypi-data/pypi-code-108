'''_1602.py

EnumWithSelectedValue
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_ARRAY = python_net_import('System', 'Array')
_ENUM_WITH_SELECTED_VALUE = python_net_import('SMT.MastaAPI.Utility.Property', 'EnumWithSelectedValue')


__docformat__ = 'restructuredtext en'
__all__ = ('EnumWithSelectedValue',)


TAPIEnum = TypeVar('TAPIEnum')


class EnumWithSelectedValue(Generic[TAPIEnum]):
    '''EnumWithSelectedValue

    This is a mastapy class.

    Generic Types:
        TAPIEnum
    '''

    TYPE = _ENUM_WITH_SELECTED_VALUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EnumWithSelectedValue.TYPE'):
        self.wrapped = instance_to_wrap
        self._freeze()

    __frozen = False

    def __setattr__(self, attr, value):
        prop = getattr(self.__class__, attr, None)
        if isinstance(prop, property):
            prop.fset(self, value)
        else:
            if self.__frozen and attr not in self.__dict__:
                raise AttributeError((
                    'Attempted to set unknown '
                    'attribute: \'{}\''.format(attr))) from None

            super().__setattr__(attr, value)

    def __delattr__(self, name):
        raise AttributeError(
            'Cannot delete the attributes of a mastapy object.') from None

    def _freeze(self):
        self.__frozen = True

    @property
    def selected_value(self) -> 'TAPIEnum':
        '''TAPIEnum: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SelectedValue

    @property
    def available_values(self) -> 'List[TAPIEnum]':
        '''List[TAPIEnum]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AvailableValues)
        return value

    def initialize_lifetime_service(self) -> 'object':
        ''' 'InitializeLifetimeService' is the original name of this method.

        Returns:
            object
        '''

        method_result = self.wrapped.InitializeLifetimeService()
        return method_result
