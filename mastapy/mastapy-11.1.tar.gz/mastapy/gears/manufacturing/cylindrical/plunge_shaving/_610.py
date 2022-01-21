'''_610.py

PlungeShaverInputsAndMicroGeometry
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _606, _605, _613
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVER_INPUTS_AND_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'PlungeShaverInputsAndMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShaverInputsAndMicroGeometry',)


class PlungeShaverInputsAndMicroGeometry(_0.APIBase):
    '''PlungeShaverInputsAndMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVER_INPUTS_AND_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShaverInputsAndMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def do_both_flanks_have_the_same_micro_geometry(self) -> 'bool':
        '''bool: 'DoBothFlanksHaveTheSameMicroGeometry' is the original name of this property.'''

        return self.wrapped.DoBothFlanksHaveTheSameMicroGeometry

    @do_both_flanks_have_the_same_micro_geometry.setter
    def do_both_flanks_have_the_same_micro_geometry(self, value: 'bool'):
        self.wrapped.DoBothFlanksHaveTheSameMicroGeometry = bool(value) if value else False

    @property
    def micro_geometry_source(self) -> 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionType':
        '''enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionType: 'MicroGeometrySource' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MicroGeometrySource, value) if self.wrapped.MicroGeometrySource is not None else None

    @micro_geometry_source.setter
    def micro_geometry_source(self, value: 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MicroGeometrySource = value

    @property
    def profile_measurement_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod: 'ProfileMeasurementMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ProfileMeasurementMethod, value) if self.wrapped.ProfileMeasurementMethod is not None else None

    @profile_measurement_method.setter
    def profile_measurement_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ProfileMeasurementMethod = value

    @property
    def lead_measurement_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod: 'LeadMeasurementMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LeadMeasurementMethod, value) if self.wrapped.LeadMeasurementMethod is not None else None

    @lead_measurement_method.setter
    def lead_measurement_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_MicroGeometryDefinitionMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LeadMeasurementMethod = value

    @property
    def number_of_points_of_interest(self) -> 'int':
        '''int: 'NumberOfPointsOfInterest' is the original name of this property.'''

        return self.wrapped.NumberOfPointsOfInterest

    @number_of_points_of_interest.setter
    def number_of_points_of_interest(self, value: 'int'):
        self.wrapped.NumberOfPointsOfInterest = int(value) if value else 0

    @property
    def points_of_interest_left_flank(self) -> 'List[_613.PointOfInterest]':
        '''List[PointOfInterest]: 'PointsOfInterestLeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointsOfInterestLeftFlank, constructor.new(_613.PointOfInterest))
        return value

    @property
    def points_of_interest_right_flank(self) -> 'List[_613.PointOfInterest]':
        '''List[PointOfInterest]: 'PointsOfInterestRightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointsOfInterestRightFlank, constructor.new(_613.PointOfInterest))
        return value

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
