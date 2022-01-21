'''_2097.py

AlignConnectedComponentOptions
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value
from mastapy.system_model.fe import _2108
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.math_utility import _1290, _1289
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ALIGN_CONNECTED_COMPONENT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'AlignConnectedComponentOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('AlignConnectedComponentOptions',)


class AlignConnectedComponentOptions(_0.APIBase):
    '''AlignConnectedComponentOptions

    This is a mastapy class.
    '''

    TYPE = _ALIGN_CONNECTED_COMPONENT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AlignConnectedComponentOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_orientation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ComponentOrientationOption':
        '''enum_with_selected_value.EnumWithSelectedValue_ComponentOrientationOption: 'ComponentOrientation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ComponentOrientationOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ComponentOrientation, value) if self.wrapped.ComponentOrientation is not None else None

    @component_orientation.setter
    def component_orientation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ComponentOrientationOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ComponentOrientationOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ComponentOrientation = value

    @property
    def first_component_alignment_axis(self) -> '_1290.Axis':
        '''Axis: 'FirstComponentAlignmentAxis' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FirstComponentAlignmentAxis)
        return constructor.new(_1290.Axis)(value) if value is not None else None

    @first_component_alignment_axis.setter
    def first_component_alignment_axis(self, value: '_1290.Axis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FirstComponentAlignmentAxis = value

    @property
    def second_component_alignment_axis(self) -> 'enum_with_selected_value.EnumWithSelectedValue_Axis':
        '''enum_with_selected_value.EnumWithSelectedValue_Axis: 'SecondComponentAlignmentAxis' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_Axis.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SecondComponentAlignmentAxis, value) if self.wrapped.SecondComponentAlignmentAxis is not None else None

    @second_component_alignment_axis.setter
    def second_component_alignment_axis(self, value: 'enum_with_selected_value.EnumWithSelectedValue_Axis.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_Axis.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SecondComponentAlignmentAxis = value

    @property
    def first_fe_alignment_axis(self) -> '_1289.AlignmentAxis':
        '''AlignmentAxis: 'FirstFEAlignmentAxis' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FirstFEAlignmentAxis)
        return constructor.new(_1289.AlignmentAxis)(value) if value is not None else None

    @first_fe_alignment_axis.setter
    def first_fe_alignment_axis(self, value: '_1289.AlignmentAxis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FirstFEAlignmentAxis = value

    @property
    def second_fe_alignment_axis(self) -> 'enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis':
        '''enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis: 'SecondFEAlignmentAxis' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SecondFEAlignmentAxis, value) if self.wrapped.SecondFEAlignmentAxis is not None else None

    @second_fe_alignment_axis.setter
    def second_fe_alignment_axis(self, value: 'enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SecondFEAlignmentAxis = value

    @property
    def component_direction_normal_to_surface(self) -> '_1290.Axis':
        '''Axis: 'ComponentDirectionNormalToSurface' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ComponentDirectionNormalToSurface)
        return constructor.new(_1290.Axis)(value) if value is not None else None

    @component_direction_normal_to_surface.setter
    def component_direction_normal_to_surface(self, value: '_1290.Axis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ComponentDirectionNormalToSurface = value

    @property
    def perpendicular_component_alignment_axis(self) -> 'enum_with_selected_value.EnumWithSelectedValue_Axis':
        '''enum_with_selected_value.EnumWithSelectedValue_Axis: 'PerpendicularComponentAlignmentAxis' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_Axis.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.PerpendicularComponentAlignmentAxis, value) if self.wrapped.PerpendicularComponentAlignmentAxis is not None else None

    @perpendicular_component_alignment_axis.setter
    def perpendicular_component_alignment_axis(self, value: 'enum_with_selected_value.EnumWithSelectedValue_Axis.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_Axis.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.PerpendicularComponentAlignmentAxis = value

    @property
    def fe_axis_approximately_in_perpendicular_direction(self) -> '_1289.AlignmentAxis':
        '''AlignmentAxis: 'FEAxisApproximatelyInPerpendicularDirection' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FEAxisApproximatelyInPerpendicularDirection)
        return constructor.new(_1289.AlignmentAxis)(value) if value is not None else None

    @fe_axis_approximately_in_perpendicular_direction.setter
    def fe_axis_approximately_in_perpendicular_direction(self, value: '_1289.AlignmentAxis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FEAxisApproximatelyInPerpendicularDirection = value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def align_component(self):
        ''' 'AlignComponent' is the original name of this method.'''

        self.wrapped.AlignComponent()

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
