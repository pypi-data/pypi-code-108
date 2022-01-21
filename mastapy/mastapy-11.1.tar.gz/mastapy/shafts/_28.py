'''_28.py

ShaftPointStressCycleReporting
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.shafts import _27
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_POINT_STRESS_CYCLE_REPORTING = python_net_import('SMT.MastaAPI.Shafts', 'ShaftPointStressCycleReporting')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftPointStressCycleReporting',)


class ShaftPointStressCycleReporting(_0.APIBase):
    '''ShaftPointStressCycleReporting

    This is a mastapy class.
    '''

    TYPE = _SHAFT_POINT_STRESS_CYCLE_REPORTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftPointStressCycleReporting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_cycles(self) -> 'float':
        '''float: 'NumberOfCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCycles

    @property
    def equivalent_alternating_stress(self) -> 'float':
        '''float: 'EquivalentAlternatingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentAlternatingStress

    @property
    def fatigue_strength(self) -> 'float':
        '''float: 'FatigueStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueStrength

    @property
    def nominal_stress(self) -> '_27.ShaftPointStressCycle':
        '''ShaftPointStressCycle: 'NominalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_27.ShaftPointStressCycle)(self.wrapped.NominalStress) if self.wrapped.NominalStress is not None else None

    @property
    def stress(self) -> '_27.ShaftPointStressCycle':
        '''ShaftPointStressCycle: 'Stress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_27.ShaftPointStressCycle)(self.wrapped.Stress) if self.wrapped.Stress is not None else None

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
