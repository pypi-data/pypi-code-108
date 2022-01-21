'''_1339.py

InputSetter
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy.math_utility.optimisation import _1346
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INPUT_SETTER = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'InputSetter')


__docformat__ = 'restructuredtext en'
__all__ = ('InputSetter',)


T = TypeVar('T')


class InputSetter(_0.APIBase, Generic[T]):
    '''InputSetter

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _INPUT_SETTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InputSetter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fix_this_property(self) -> 'bool':
        '''bool: 'FixThisProperty' is the original name of this property.'''

        return self.wrapped.FixThisProperty

    @fix_this_property.setter
    def fix_this_property(self, value: 'bool'):
        self.wrapped.FixThisProperty = bool(value) if value else False

    @property
    def last_path_object_name(self) -> 'str':
        '''str: 'LastPathObjectName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LastPathObjectName

    @property
    def value(self) -> 'float':
        '''float: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Value

    @property
    def optimiser_input(self) -> '_1346.ParetoOptimisationInput':
        '''ParetoOptimisationInput: 'OptimiserInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1346.ParetoOptimisationInput)(self.wrapped.OptimiserInput) if self.wrapped.OptimiserInput is not None else None

    @property
    def candidate(self) -> 'T':
        '''T: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Candidate

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
