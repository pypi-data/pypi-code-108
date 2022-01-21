'''_1611.py

NamedRangeWithOverridableMinAndMax
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_NAMED_RANGE_WITH_OVERRIDABLE_MIN_AND_MAX = python_net_import('SMT.MastaAPI.Utility.Property', 'NamedRangeWithOverridableMinAndMax')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedRangeWithOverridableMinAndMax',)


T = TypeVar('T')
TMeasurement = TypeVar('TMeasurement', bound='_1398.MeasurementBase')


class NamedRangeWithOverridableMinAndMax(_0.APIBase, Generic[T, TMeasurement]):
    '''NamedRangeWithOverridableMinAndMax

    This is a mastapy class.

    Generic Types:
        T
        TMeasurement
    '''

    TYPE = _NAMED_RANGE_WITH_OVERRIDABLE_MIN_AND_MAX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedRangeWithOverridableMinAndMax.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def min(self) -> 'overridable.Overridable_T':
        '''overridable.Overridable_T: 'Min' is the original name of this property.'''

        return constructor.new(overridable.Overridable_T)(self.wrapped.Min) if self.wrapped.Min is not None else None

    @min.setter
    def min(self, value: 'overridable.Overridable_T.implicit_type()'):
        wrapper_type = overridable.Overridable_T.wrapper_type()
        enclosed_type = overridable.Overridable_T.implicit_type()
        value, is_overridden = _unpack_overridable(value.wrapped)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.Min = value

    @property
    def max(self) -> 'overridable.Overridable_T':
        '''overridable.Overridable_T: 'Max' is the original name of this property.'''

        return constructor.new(overridable.Overridable_T)(self.wrapped.Max) if self.wrapped.Max is not None else None

    @max.setter
    def max(self, value: 'overridable.Overridable_T.implicit_type()'):
        wrapper_type = overridable.Overridable_T.wrapper_type()
        enclosed_type = overridable.Overridable_T.implicit_type()
        value, is_overridden = _unpack_overridable(value.wrapped)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.Max = value

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
