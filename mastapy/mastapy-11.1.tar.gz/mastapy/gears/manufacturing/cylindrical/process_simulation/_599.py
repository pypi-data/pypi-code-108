'''_599.py

CutterProcessSimulation
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CUTTER_PROCESS_SIMULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.ProcessSimulation', 'CutterProcessSimulation')


__docformat__ = 'restructuredtext en'
__all__ = ('CutterProcessSimulation',)


class CutterProcessSimulation(_0.APIBase):
    '''CutterProcessSimulation

    This is a mastapy class.
    '''

    TYPE = _CUTTER_PROCESS_SIMULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CutterProcessSimulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_teeth_to_calculate(self) -> 'int':
        '''int: 'NumberOfTeethToCalculate' is the original name of this property.'''

        return self.wrapped.NumberOfTeethToCalculate

    @number_of_teeth_to_calculate.setter
    def number_of_teeth_to_calculate(self, value: 'int'):
        self.wrapped.NumberOfTeethToCalculate = int(value) if value else 0

    @property
    def start_of_measured_lead(self) -> 'float':
        '''float: 'StartOfMeasuredLead' is the original name of this property.'''

        return self.wrapped.StartOfMeasuredLead

    @start_of_measured_lead.setter
    def start_of_measured_lead(self, value: 'float'):
        self.wrapped.StartOfMeasuredLead = float(value) if value else 0.0

    @property
    def end_of_measured_lead(self) -> 'float':
        '''float: 'EndOfMeasuredLead' is the original name of this property.'''

        return self.wrapped.EndOfMeasuredLead

    @end_of_measured_lead.setter
    def end_of_measured_lead(self, value: 'float'):
        self.wrapped.EndOfMeasuredLead = float(value) if value else 0.0

    @property
    def start_of_measured_profile(self) -> 'float':
        '''float: 'StartOfMeasuredProfile' is the original name of this property.'''

        return self.wrapped.StartOfMeasuredProfile

    @start_of_measured_profile.setter
    def start_of_measured_profile(self, value: 'float'):
        self.wrapped.StartOfMeasuredProfile = float(value) if value else 0.0

    @property
    def end_of_measured_profile(self) -> 'float':
        '''float: 'EndOfMeasuredProfile' is the original name of this property.'''

        return self.wrapped.EndOfMeasuredProfile

    @end_of_measured_profile.setter
    def end_of_measured_profile(self, value: 'float'):
        self.wrapped.EndOfMeasuredProfile = float(value) if value else 0.0

    @property
    def rolling_distance_per_step(self) -> 'float':
        '''float: 'RollingDistancePerStep' is the original name of this property.'''

        return self.wrapped.RollingDistancePerStep

    @rolling_distance_per_step.setter
    def rolling_distance_per_step(self, value: 'float'):
        self.wrapped.RollingDistancePerStep = float(value) if value else 0.0

    @property
    def lead_distance_per_step(self) -> 'float':
        '''float: 'LeadDistancePerStep' is the original name of this property.'''

        return self.wrapped.LeadDistancePerStep

    @lead_distance_per_step.setter
    def lead_distance_per_step(self, value: 'float'):
        self.wrapped.LeadDistancePerStep = float(value) if value else 0.0

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
