'''_622.py

CalculateProfileDeviationAccuracy
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _638
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CALCULATE_PROFILE_DEVIATION_ACCURACY = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'CalculateProfileDeviationAccuracy')


__docformat__ = 'restructuredtext en'
__all__ = ('CalculateProfileDeviationAccuracy',)


class CalculateProfileDeviationAccuracy(_0.APIBase):
    '''CalculateProfileDeviationAccuracy

    This is a mastapy class.
    '''

    TYPE = _CALCULATE_PROFILE_DEVIATION_ACCURACY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CalculateProfileDeviationAccuracy.TYPE'):
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
    def total_profile_deviation(self) -> 'float':
        '''float: 'TotalProfileDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalProfileDeviation

    @property
    def profile_form_deviation(self) -> 'float':
        '''float: 'ProfileFormDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormDeviation

    @property
    def profile_slope_deviation(self) -> 'float':
        '''float: 'ProfileSlopeDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileSlopeDeviation

    @property
    def profile_deviation_iso132811995e_quality_grade_designed(self) -> 'float':
        '''float: 'ProfileDeviationISO132811995EQualityGradeDesigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileDeviationISO132811995EQualityGradeDesigned

    @property
    def profile_deviation_ansiagma20151a01_quality_grade_designed(self) -> 'float':
        '''float: 'ProfileDeviationANSIAGMA20151A01QualityGradeDesigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileDeviationANSIAGMA20151A01QualityGradeDesigned

    @property
    def total_profile_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'TotalProfileDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalProfileDeviationISO132811995EQualityGradeObtained

    @property
    def profile_form_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'ProfileFormDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormDeviationISO132811995EQualityGradeObtained

    @property
    def profile_slope_deviation_iso132811995e_quality_grade_obtained(self) -> 'float':
        '''float: 'ProfileSlopeDeviationISO132811995EQualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileSlopeDeviationISO132811995EQualityGradeObtained

    @property
    def total_profile_deviation_ansiagma20151a01_quality_grade_obtained(self) -> 'float':
        '''float: 'TotalProfileDeviationANSIAGMA20151A01QualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalProfileDeviationANSIAGMA20151A01QualityGradeObtained

    @property
    def profile_form_deviation_ansiagma20151a01_quality_grade_obtained(self) -> 'float':
        '''float: 'ProfileFormDeviationANSIAGMA20151A01QualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormDeviationANSIAGMA20151A01QualityGradeObtained

    @property
    def profile_slope_deviation_ansiagma20151a01_quality_grade_obtained(self) -> 'float':
        '''float: 'ProfileSlopeDeviationANSIAGMA20151A01QualityGradeObtained' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileSlopeDeviationANSIAGMA20151A01QualityGradeObtained

    @property
    def achieved_profile_iso132811995e_quality_grade(self) -> 'float':
        '''float: 'AchievedProfileISO132811995EQualityGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedProfileISO132811995EQualityGrade

    @property
    def achieved_profile_ansiagma20151a01_quality_grade(self) -> 'float':
        '''float: 'AchievedProfileANSIAGMA20151A01QualityGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedProfileANSIAGMA20151A01QualityGrade

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
