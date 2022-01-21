'''_621.py

CalculatePitchDeviationAccuracy
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _638
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CALCULATE_PITCH_DEVIATION_ACCURACY = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'CalculatePitchDeviationAccuracy')


__docformat__ = 'restructuredtext en'
__all__ = ('CalculatePitchDeviationAccuracy',)


class CalculatePitchDeviationAccuracy(_0.APIBase):
    '''CalculatePitchDeviationAccuracy

    This is a mastapy class.
    '''

    TYPE = _CALCULATE_PITCH_DEVIATION_ACCURACY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CalculatePitchDeviationAccuracy.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flank_name(self) -> 'str':
        '''str: 'FlankName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankName

    @property
    def pitch_deviation_iso132811995e_quality_grade_designed(self) -> 'float':
        '''float: 'PitchDeviationISO132811995EQualityGradeDesigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDeviationISO132811995EQualityGradeDesigned

    @property
    def pitch_deviation_ansiagma20151a01_quality_grade_designed(self) -> 'float':
        '''float: 'PitchDeviationANSIAGMA20151A01QualityGradeDesigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDeviationANSIAGMA20151A01QualityGradeDesigned

    @property
    def single_pitch_deviation(self) -> 'float':
        '''float: 'SinglePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchDeviation

    @property
    def cumulative_pitch_deviation(self) -> 'float':
        '''float: 'CumulativePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CumulativePitchDeviation

    @property
    def total_cumulative_pitch_deviation(self) -> 'float':
        '''float: 'TotalCumulativePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalCumulativePitchDeviation

    @property
    def total_cumulative_pitch_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'TotalCumulativePitchDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalCumulativePitchDeviationISO132811995EQualityGradeObtained

    @property
    def cumulative_pitch_deviation_ansiagma20151a01_quality_grade_obtained(self) -> 'float':
        '''float: 'CumulativePitchDeviationANSIAGMA20151A01QualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CumulativePitchDeviationANSIAGMA20151A01QualityGradeObtained

    @property
    def cumulative_pitch_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'CumulativePitchDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CumulativePitchDeviationISO132811995EQualityGradeObtained

    @property
    def single_pitch_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'SinglePitchDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchDeviationISO132811995EQualityGradeObtained

    @property
    def single_pitch_deviation_ansiagma20151a01_quality_grade_obtained(self) -> 'float':
        '''float: 'SinglePitchDeviationANSIAGMA20151A01QualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchDeviationANSIAGMA20151A01QualityGradeObtained

    @property
    def achieved_pitch_iso132811995e_quality_grade(self) -> 'float':
        '''float: 'AchievedPitchISO132811995EQualityGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedPitchISO132811995EQualityGrade

    @property
    def achieved_pitch_ansiagma20151a01_quality_grade(self) -> 'float':
        '''float: 'AchievedPitchANSIAGMA20151A01QualityGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedPitchANSIAGMA20151A01QualityGrade

    @property
    def manufactured_iso132811995e_quality_grades(self) -> 'List[_638.ManufacturedQualityGrade]':
        '''List[ManufacturedQualityGrade]: 'ManufacturedISO132811995EQualityGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ManufacturedISO132811995EQualityGrades, constructor.new(_638.ManufacturedQualityGrade))
        return value

    @property
    def manufactured_ansiagma20151a01_quality_grades(self) -> 'List[_638.ManufacturedQualityGrade]':
        '''List[ManufacturedQualityGrade]: 'ManufacturedANSIAGMA20151A01QualityGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ManufacturedANSIAGMA20151A01QualityGrades, constructor.new(_638.ManufacturedQualityGrade))
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
