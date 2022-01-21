'''_2578.py

FlexibleGearChart
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.analyses_and_results.system_deflections import _2480
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility_gui.charts import _1620
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_GEAR_CHART = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'FlexibleGearChart')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexibleGearChart',)


class FlexibleGearChart(_0.APIBase):
    '''FlexibleGearChart

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_GEAR_CHART

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexibleGearChart.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def remove_rigid_body_motion(self) -> 'bool':
        '''bool: 'RemoveRigidBodyMotion' is the original name of this property.'''

        return self.wrapped.RemoveRigidBodyMotion

    @remove_rigid_body_motion.setter
    def remove_rigid_body_motion(self, value: 'bool'):
        self.wrapped.RemoveRigidBodyMotion = bool(value) if value else False

    @property
    def planets(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection: 'Planets' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection)(self.wrapped.Planets) if self.wrapped.Planets is not None else None

    @planets.setter
    def planets(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearSystemDeflection.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.Planets = value

    @property
    def chart(self) -> '_1620.LegacyChartMathChartDefinition':
        '''LegacyChartMathChartDefinition: 'Chart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1620.LegacyChartMathChartDefinition)(self.wrapped.Chart) if self.wrapped.Chart is not None else None

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
