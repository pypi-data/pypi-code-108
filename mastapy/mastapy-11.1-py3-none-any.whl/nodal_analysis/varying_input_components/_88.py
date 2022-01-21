'''_88.py

AbstractVaryingInputComponent
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value
from mastapy.nodal_analysis import _86
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.math_utility import _1333
from mastapy.math_utility.measured_data import _1365
from mastapy.nodal_analysis.varying_input_components import _93
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_VARYING_INPUT_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.VaryingInputComponents', 'AbstractVaryingInputComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractVaryingInputComponent',)


class AbstractVaryingInputComponent(_0.APIBase):
    '''AbstractVaryingInputComponent

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_VARYING_INPUT_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractVaryingInputComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def input_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ValueInputOption':
        '''enum_with_selected_value.EnumWithSelectedValue_ValueInputOption: 'InputType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ValueInputOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.InputType, value) if self.wrapped.InputType is not None else None

    @input_type.setter
    def input_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ValueInputOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ValueInputOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.InputType = value

    @property
    def value_vs_time(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ValueVsTime' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ValueVsTime) if self.wrapped.ValueVsTime is not None else None

    @value_vs_time.setter
    def value_vs_time(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ValueVsTime = value

    @property
    def value_vs_angle(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ValueVsAngle' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ValueVsAngle) if self.wrapped.ValueVsAngle is not None else None

    @value_vs_angle.setter
    def value_vs_angle(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ValueVsAngle = value

    @property
    def value_vs_angle_and_speed(self) -> '_1365.GriddedSurfaceAccessor':
        '''GriddedSurfaceAccessor: 'ValueVsAngleAndSpeed' is the original name of this property.'''

        return constructor.new(_1365.GriddedSurfaceAccessor)(self.wrapped.ValueVsAngleAndSpeed) if self.wrapped.ValueVsAngleAndSpeed is not None else None

    @value_vs_angle_and_speed.setter
    def value_vs_angle_and_speed(self, value: '_1365.GriddedSurfaceAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ValueVsAngleAndSpeed = value

    @property
    def value_vs_position(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ValueVsPosition' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ValueVsPosition) if self.wrapped.ValueVsPosition is not None else None

    @value_vs_position.setter
    def value_vs_position(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ValueVsPosition = value

    @property
    def time_profile_repeats(self) -> 'bool':
        '''bool: 'TimeProfileRepeats' is the original name of this property.'''

        return self.wrapped.TimeProfileRepeats

    @time_profile_repeats.setter
    def time_profile_repeats(self, value: 'bool'):
        self.wrapped.TimeProfileRepeats = bool(value) if value else False

    @property
    def single_point_selection_method_for_value_vs_time(self) -> 'enum_with_selected_value.EnumWithSelectedValue_SinglePointSelectionMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_SinglePointSelectionMethod: 'SinglePointSelectionMethodForValueVsTime' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_SinglePointSelectionMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SinglePointSelectionMethodForValueVsTime, value) if self.wrapped.SinglePointSelectionMethodForValueVsTime is not None else None

    @single_point_selection_method_for_value_vs_time.setter
    def single_point_selection_method_for_value_vs_time(self, value: 'enum_with_selected_value.EnumWithSelectedValue_SinglePointSelectionMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_SinglePointSelectionMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SinglePointSelectionMethodForValueVsTime = value

    @property
    def include_values_before_zero_time(self) -> 'bool':
        '''bool: 'IncludeValuesBeforeZeroTime' is the original name of this property.'''

        return self.wrapped.IncludeValuesBeforeZeroTime

    @include_values_before_zero_time.setter
    def include_values_before_zero_time(self, value: 'bool'):
        self.wrapped.IncludeValuesBeforeZeroTime = bool(value) if value else False

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
