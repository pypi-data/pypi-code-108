'''enum_with_selected_value_runtime.py

This module holds methods for creating mastapy's EnumWithSelectedValue
type. We have to do this quite differently in Python compared to the original
C#. This logic is only used during runtime - intellisense relies on definitions
present in mastapy._internal.implicit.enum_with_selected_value.
'''

from mastapy._internal import conversion, constructor
from mastapy._internal.python_net import python_net_import

ENUM_WITH_SELECTED_VALUE = python_net_import(
    'SMT.MastaAPI.Utility.Property', 'EnumWithSelectedValue')


__docformat__ = 'restructuredtext en'
__all__ = ('create',)


def _selected_value(self):
    value = conversion.pn_to_mp_enum(self.enclosing.SelectedValue)
    return constructor.new(type(self))(value) if value else None


def _available_values(self):
    return conversion.pn_to_mp_objects_in_list(
        self.enclosing.AvailableValues,
        constructor.new(type(self)))


def create(pn_enum, enum_type):
    '''Creates an altered enum with additional data and methods
    present. Mimics EnumWithSelectedValue from C#. We had to do it this way
    because we can't use the custom constructor logic we need inside of
    a subclass of enum's constructor.

    Args:
        pn_enum: PythonNet enum
        enum_type: the enum_type to create

    Returns:
        an enum of type enum_type (with modifications)
    '''

    enum_type.selected_value = property(_selected_value)
    enum_type.available_values = property(_available_values)

    int_value = pn_enum.SelectedValue
    enum_value = enum_type(int_value)

    # Note: We are directly entering into __dict__ rather than
    # setting an attribute (e.g. enum_value.enclosing) to avoid calling
    # __setattr__
    enum_value.__dict__['enclosing'] = pn_enum
    enum_value.__dict__['wrapped'] = int_value

    return enum_value
