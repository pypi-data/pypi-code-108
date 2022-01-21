'''_900.py

TableFilter
'''


from typing import List, Generic, TypeVar

from mastapy.math_utility import _1287
from mastapy._internal import constructor, conversion
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy.gears.analysis import _1161
from mastapy._internal.python_net import python_net_import

_TABLE_FILTER = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'TableFilter')


__docformat__ = 'restructuredtext en'
__all__ = ('TableFilter',)


TAnalysis = TypeVar('TAnalysis', bound='_1161.AbstractGearSetAnalysis')
TCandidate = TypeVar('TCandidate')


class TableFilter(_0.APIBase, Generic[TAnalysis, TCandidate]):
    '''TableFilter

    This is a mastapy class.

    Generic Types:
        TAnalysis
        TCandidate
    '''

    TYPE = _TABLE_FILTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TableFilter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def range(self) -> '_1287.Range':
        '''Range: 'Range' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.Range.__class__.__mro__:
            raise CastException('Failed to cast range to Range. Expected: {}.'.format(self.wrapped.Range.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Range.__class__)(self.wrapped.Range) if self.wrapped.Range is not None else None

    @range.setter
    def range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.Range = value

    @property
    def unit(self) -> 'str':
        '''str: 'Unit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Unit

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def remove_filter(self):
        ''' 'RemoveFilter' is the original name of this method.'''

        self.wrapped.RemoveFilter()

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
