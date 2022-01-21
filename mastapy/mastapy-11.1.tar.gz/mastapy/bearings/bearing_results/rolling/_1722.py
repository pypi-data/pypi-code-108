'''_1722.py

DIN732Results
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DIN732_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'DIN732Results')


__docformat__ = 'restructuredtext en'
__all__ = ('DIN732Results',)


class DIN732Results(_0.APIBase):
    '''DIN732Results

    This is a mastapy class.
    '''

    TYPE = _DIN732_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DIN732Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dynamic_equivalent_load(self) -> 'float':
        '''float: 'DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicEquivalentLoad

    @property
    def heat_dissipation_capacity_of_bearing_lubrication(self) -> 'float':
        '''float: 'HeatDissipationCapacityOfBearingLubrication' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeatDissipationCapacityOfBearingLubrication

    @property
    def required_oil_flow_rate(self) -> 'float':
        '''float: 'RequiredOilFlowRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredOilFlowRate

    @property
    def frictional_power_loss(self) -> 'float':
        '''float: 'FrictionalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalPowerLoss

    @property
    def speed_dependent_frictional_power_loss(self) -> 'float':
        '''float: 'SpeedDependentFrictionalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpeedDependentFrictionalPowerLoss

    @property
    def load_dependent_frictional_power_loss(self) -> 'float':
        '''float: 'LoadDependentFrictionalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDependentFrictionalPowerLoss

    @property
    def thermal_limiting_speed(self) -> 'float':
        '''float: 'ThermalLimitingSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalLimitingSpeed

    @property
    def thermal_reference_speed(self) -> 'float':
        '''float: 'ThermalReferenceSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalReferenceSpeed

    @property
    def thermal_reference_speed_f0r(self) -> 'float':
        '''float: 'ThermalReferenceSpeedF0r' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalReferenceSpeedF0r

    @property
    def thermal_reference_speed_f1r(self) -> 'float':
        '''float: 'ThermalReferenceSpeedF1r' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalReferenceSpeedF1r

    @property
    def thermal_limiting_speed_f0(self) -> 'float':
        '''float: 'ThermalLimitingSpeedF0' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalLimitingSpeedF0

    @property
    def thermal_limiting_speed_f1(self) -> 'float':
        '''float: 'ThermalLimitingSpeedF1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalLimitingSpeedF1

    @property
    def limiting_speed_warning(self) -> 'str':
        '''str: 'LimitingSpeedWarning' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitingSpeedWarning

    @property
    def reference_speed_warning(self) -> 'str':
        '''str: 'ReferenceSpeedWarning' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceSpeedWarning

    @property
    def air_convection_heat_dissipation(self) -> 'float':
        '''float: 'AirConvectionHeatDissipation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AirConvectionHeatDissipation

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
