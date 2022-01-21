'''_637.py

HobResharpeningError
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_HOB_RESHARPENING_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'HobResharpeningError')


__docformat__ = 'restructuredtext en'
__all__ = ('HobResharpeningError',)


class HobResharpeningError(_0.APIBase):
    '''HobResharpeningError

    This is a mastapy class.
    '''

    TYPE = _HOB_RESHARPENING_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HobResharpeningError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radial_alignment_error_reading(self) -> 'float':
        '''float: 'RadialAlignmentErrorReading' is the original name of this property.'''

        return self.wrapped.RadialAlignmentErrorReading

    @radial_alignment_error_reading.setter
    def radial_alignment_error_reading(self, value: 'float'):
        self.wrapped.RadialAlignmentErrorReading = float(value) if value else 0.0

    @property
    def radial_alignment_measurement_length(self) -> 'float':
        '''float: 'RadialAlignmentMeasurementLength' is the original name of this property.'''

        return self.wrapped.RadialAlignmentMeasurementLength

    @radial_alignment_measurement_length.setter
    def radial_alignment_measurement_length(self, value: 'float'):
        self.wrapped.RadialAlignmentMeasurementLength = float(value) if value else 0.0

    @property
    def total_gash_indexing_variation(self) -> 'float':
        '''float: 'TotalGashIndexingVariation' is the original name of this property.'''

        return self.wrapped.TotalGashIndexingVariation

    @total_gash_indexing_variation.setter
    def total_gash_indexing_variation(self, value: 'float'):
        self.wrapped.TotalGashIndexingVariation = float(value) if value else 0.0

    @property
    def use_sin_curve_for_gash_index_variation(self) -> 'bool':
        '''bool: 'UseSinCurveForGashIndexVariation' is the original name of this property.'''

        return self.wrapped.UseSinCurveForGashIndexVariation

    @use_sin_curve_for_gash_index_variation.setter
    def use_sin_curve_for_gash_index_variation(self, value: 'bool'):
        self.wrapped.UseSinCurveForGashIndexVariation = bool(value) if value else False

    @property
    def gash_lead_error_reading(self) -> 'float':
        '''float: 'GashLeadErrorReading' is the original name of this property.'''

        return self.wrapped.GashLeadErrorReading

    @gash_lead_error_reading.setter
    def gash_lead_error_reading(self, value: 'float'):
        self.wrapped.GashLeadErrorReading = float(value) if value else 0.0

    @property
    def gash_lead_measurement_length(self) -> 'float':
        '''float: 'GashLeadMeasurementLength' is the original name of this property.'''

        return self.wrapped.GashLeadMeasurementLength

    @gash_lead_measurement_length.setter
    def gash_lead_measurement_length(self, value: 'float'):
        self.wrapped.GashLeadMeasurementLength = float(value) if value else 0.0

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
