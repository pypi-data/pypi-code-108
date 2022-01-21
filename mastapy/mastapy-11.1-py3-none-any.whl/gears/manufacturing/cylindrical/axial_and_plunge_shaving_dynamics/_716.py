'''_716.py

PlungeShaverDynamicSettings
'''


from typing import List

from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVER_DYNAMIC_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'PlungeShaverDynamicSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShaverDynamicSettings',)


class PlungeShaverDynamicSettings(_0.APIBase):
    '''PlungeShaverDynamicSettings

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVER_DYNAMIC_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShaverDynamicSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def calculation_accuracy(self) -> 'PlungeShaverDynamicSettings.PlungeShavingDynamicAccuracy':
        '''PlungeShavingDynamicAccuracy: 'CalculationAccuracy' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CalculationAccuracy)
        return constructor.new(PlungeShaverDynamicSettings.PlungeShavingDynamicAccuracy)(value) if value is not None else None

    @calculation_accuracy.setter
    def calculation_accuracy(self, value: 'PlungeShaverDynamicSettings.PlungeShavingDynamicAccuracy'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CalculationAccuracy = value

    @property
    def calculation_flank(self) -> 'PlungeShaverDynamicSettings.PlungeShavingDynamicFlank':
        '''PlungeShavingDynamicFlank: 'CalculationFlank' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CalculationFlank)
        return constructor.new(PlungeShaverDynamicSettings.PlungeShavingDynamicFlank)(value) if value is not None else None

    @calculation_flank.setter
    def calculation_flank(self, value: 'PlungeShaverDynamicSettings.PlungeShavingDynamicFlank'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CalculationFlank = value

    @property
    def section_locations(self) -> 'PlungeShaverDynamicSettings.PlungeShavingDynamicsSection':
        '''PlungeShavingDynamicsSection: 'SectionLocations' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SectionLocations)
        return constructor.new(PlungeShaverDynamicSettings.PlungeShavingDynamicsSection)(value) if value is not None else None

    @section_locations.setter
    def section_locations(self, value: 'PlungeShaverDynamicSettings.PlungeShavingDynamicsSection'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SectionLocations = value

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
