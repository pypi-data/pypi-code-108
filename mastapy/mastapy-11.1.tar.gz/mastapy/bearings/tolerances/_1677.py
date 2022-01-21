'''_1677.py

SupportTolerance
'''


from mastapy._internal.implicit import enum_with_selected_value
from mastapy.bearings.tolerances import _1666, _1678, _1665
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy._internal.python_net import python_net_import

_SUPPORT_TOLERANCE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'SupportTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('SupportTolerance',)


class SupportTolerance(_1665.InterferenceTolerance):
    '''SupportTolerance

    This is a mastapy class.
    '''

    TYPE = _SUPPORT_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SupportTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tolerance_band_designation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation':
        '''enum_with_selected_value.EnumWithSelectedValue_ITDesignation: 'ToleranceBandDesignation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ToleranceBandDesignation, value) if self.wrapped.ToleranceBandDesignation is not None else None

    @tolerance_band_designation.setter
    def tolerance_band_designation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ToleranceBandDesignation = value

    @property
    def tolerance_deviation_class(self) -> 'enum_with_selected_value.EnumWithSelectedValue_SupportToleranceLocationDesignation':
        '''enum_with_selected_value.EnumWithSelectedValue_SupportToleranceLocationDesignation: 'ToleranceDeviationClass' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_SupportToleranceLocationDesignation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ToleranceDeviationClass, value) if self.wrapped.ToleranceDeviationClass is not None else None

    @tolerance_deviation_class.setter
    def tolerance_deviation_class(self, value: 'enum_with_selected_value.EnumWithSelectedValue_SupportToleranceLocationDesignation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_SupportToleranceLocationDesignation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ToleranceDeviationClass = value
