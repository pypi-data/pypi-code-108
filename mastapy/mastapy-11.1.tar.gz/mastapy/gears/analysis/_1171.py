'''_1171.py

GearSetGroupDutyCycle
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating import _328
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_SET_GROUP_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearSetGroupDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetGroupDutyCycle',)


class GearSetGroupDutyCycle(_0.APIBase):
    '''GearSetGroupDutyCycle

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_GROUP_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetGroupDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def analysis_name(self) -> 'str':
        '''str: 'AnalysisName' is the original name of this property.'''

        return self.wrapped.AnalysisName

    @analysis_name.setter
    def analysis_name(self, value: 'str'):
        self.wrapped.AnalysisName = str(value) if value else ''

    @property
    def total_duration(self) -> 'float':
        '''float: 'TotalDuration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalDuration

    @property
    def normalized_safety_factor_for_fatigue_and_static(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForFatigueAndStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForFatigueAndStatic

    @property
    def normalized_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForFatigue

    @property
    def normalized_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForStatic

    @property
    def normalized_bending_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedBendingSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedBendingSafetyFactorForFatigue

    @property
    def normalized_bending_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedBendingSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedBendingSafetyFactorForStatic

    @property
    def normalized_contact_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedContactSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedContactSafetyFactorForFatigue

    @property
    def normalized_contact_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedContactSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedContactSafetyFactorForStatic

    @property
    def loaded_rating_duty_cycles(self) -> 'List[_328.GearSetDutyCycleRating]':
        '''List[GearSetDutyCycleRating]: 'LoadedRatingDutyCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadedRatingDutyCycles, constructor.new(_328.GearSetDutyCycleRating))
        return value

    @property
    def rating_duty_cycles(self) -> 'List[_328.GearSetDutyCycleRating]':
        '''List[GearSetDutyCycleRating]: 'RatingDutyCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RatingDutyCycles, constructor.new(_328.GearSetDutyCycleRating))
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
