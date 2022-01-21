'''_1072.py

MicroGeometryViewingOptions
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1061
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears.ltca import _787
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.nodal_analysis import _82
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_VIEWING_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'MicroGeometryViewingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryViewingOptions',)


class MicroGeometryViewingOptions(_0.APIBase):
    '''MicroGeometryViewingOptions

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_VIEWING_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryViewingOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_force_arrows(self) -> 'bool':
        '''bool: 'ShowForceArrows' is the original name of this property.'''

        return self.wrapped.ShowForceArrows

    @show_force_arrows.setter
    def show_force_arrows(self, value: 'bool'):
        self.wrapped.ShowForceArrows = bool(value) if value else False

    @property
    def show_contact_chart(self) -> 'bool':
        '''bool: 'ShowContactChart' is the original name of this property.'''

        return self.wrapped.ShowContactChart

    @show_contact_chart.setter
    def show_contact_chart(self, value: 'bool'):
        self.wrapped.ShowContactChart = bool(value) if value else False

    @property
    def show_root_stress_chart(self) -> 'bool':
        '''bool: 'ShowRootStressChart' is the original name of this property.'''

        return self.wrapped.ShowRootStressChart

    @show_root_stress_chart.setter
    def show_root_stress_chart(self, value: 'bool'):
        self.wrapped.ShowRootStressChart = bool(value) if value else False

    @property
    def show_contact_points(self) -> 'bool':
        '''bool: 'ShowContactPoints' is the original name of this property.'''

        return self.wrapped.ShowContactPoints

    @show_contact_points.setter
    def show_contact_points(self, value: 'bool'):
        self.wrapped.ShowContactPoints = bool(value) if value else False

    @property
    def gear_option(self) -> '_1061.DrawDefiningGearOrBoth':
        '''DrawDefiningGearOrBoth: 'GearOption' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.GearOption)
        return constructor.new(_1061.DrawDefiningGearOrBoth)(value) if value is not None else None

    @gear_option.setter
    def gear_option(self, value: '_1061.DrawDefiningGearOrBoth'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.GearOption = value

    @property
    def contact_results(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ContactResultType':
        '''enum_with_selected_value.EnumWithSelectedValue_ContactResultType: 'ContactResults' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ContactResultType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ContactResults, value) if self.wrapped.ContactResults is not None else None

    @contact_results.setter
    def contact_results(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ContactResultType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ContactResultType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ContactResults = value

    @property
    def root_stress_results_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_StressResultsType':
        '''enum_with_selected_value.EnumWithSelectedValue_StressResultsType: 'RootStressResultsType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_StressResultsType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.RootStressResultsType, value) if self.wrapped.RootStressResultsType is not None else None

    @root_stress_results_type.setter
    def root_stress_results_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_StressResultsType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_StressResultsType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.RootStressResultsType = value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def edit_contact_patch_legend(self):
        ''' 'EditContactPatchLegend' is the original name of this method.'''

        self.wrapped.EditContactPatchLegend()

    def edit_root_stress_legend(self):
        ''' 'EditRootStressLegend' is the original name of this method.'''

        self.wrapped.EditRootStressLegend()

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
