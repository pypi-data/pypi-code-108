'''_901.py

DesignConstraint
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.utility.model_validation import _1563
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.math_utility import _1287
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy.utility import _1384
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DESIGN_CONSTRAINT = python_net_import('SMT.MastaAPI.Gears.GearDesigns', 'DesignConstraint')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignConstraint',)


class DesignConstraint(_0.APIBase):
    '''DesignConstraint

    This is a mastapy class.
    '''

    TYPE = _DESIGN_CONSTRAINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignConstraint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def type_(self) -> 'str':
        '''str: 'Type' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Type

    @property
    def severity(self) -> 'enum_with_selected_value.EnumWithSelectedValue_Severity':
        '''enum_with_selected_value.EnumWithSelectedValue_Severity: 'Severity' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_Severity.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.Severity, value) if self.wrapped.Severity is not None else None

    @severity.setter
    def severity(self, value: 'enum_with_selected_value.EnumWithSelectedValue_Severity.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_Severity.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.Severity = value

    @property
    def property_(self) -> 'str':
        '''str: 'Property' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Property

    @property
    def range(self) -> '_1287.Range':
        '''Range: 'Range' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.Range.__class__.__mro__:
            raise CastException('Failed to cast range to Range. Expected: {}.'.format(self.wrapped.Range.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Range.__class__)(self.wrapped.Range) if self.wrapped.Range is not None else None

    @range.setter
    def range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.Range = value

    @property
    def integer_range(self) -> '_1384.IntegerRange':
        '''IntegerRange: 'IntegerRange' is the original name of this property.'''

        return constructor.new(_1384.IntegerRange)(self.wrapped.IntegerRange) if self.wrapped.IntegerRange is not None else None

    @integer_range.setter
    def integer_range(self, value: '_1384.IntegerRange'):
        value = value.wrapped if value else None
        self.wrapped.IntegerRange = value

    @property
    def unit(self) -> 'str':
        '''str: 'Unit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Unit
