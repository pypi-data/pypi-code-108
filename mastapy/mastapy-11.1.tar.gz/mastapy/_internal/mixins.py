'''mixins.py


Module containing mixins and ABCs that add methods/properties
for overridables.
'''


from collections.abc import Sequence
from enum import Enum


class OverridableMixin:
    '''Abstract class for Overridable types.

    Note:
        This does not subclass an ABC due to MetaClass conflicts.
    '''

    @property
    def value(self):
        '''Abstract method for value.'''

    @property
    def overridden(self) -> bool:
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self._wrapped.Overridden

    @property
    def override_value(self):
        '''Abstract method for override_value.'''

    @property
    def calculated_value(self):
        '''Abstract method for calculated_value.'''


class ReportingOverridableMixin:
    '''Abstract class for ReportingOverridable types.

    Note:
        This does not subclass an ABC due to MetaClass conflicts.
    '''

    @property
    def is_overridden(self) -> bool:
        '''bool: 'IsOverridden' is the original name of this property.'''

        return self._wrapped.IsOverridden

    @is_overridden.setter
    def is_overridden(self, value: bool):
        self._wrapped.IsOverridden = value if value else False

    @property
    def value(self):
        '''Abstract method for value.'''


class EnumWithSelectedValueMixin:
    '''Abstract class for EnumWithSelectedValue types.

    Note:
        This does not subclass an ABC due to MetaClass conflicts.
    '''

    @property
    def selected_value(self):
        '''Abstract method for selected_value.'''


class ListWithSelectedItemMixin(Sequence):
    '''Abstract class for ListWithSelectedItem types.'''

    @property
    def available_values(self):
        '''Abstract method for available_values.'''

    @property
    def selected_value(self):
        '''Abstract method for selected_value.'''

    def __len__(self):
        return len(self.available_values)

    def __getitem__(self, idx):
        return self.available_values[idx]
