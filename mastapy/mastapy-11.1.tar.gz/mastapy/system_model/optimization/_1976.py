'''_1976.py

CylindricalGearSetOptimizer
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.optimization import _1977
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_OPTIMIZER = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'CylindricalGearSetOptimizer')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetOptimizer',)


class CylindricalGearSetOptimizer(_0.APIBase):
    '''CylindricalGearSetOptimizer

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_OPTIMIZER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetOptimizer.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def create_new_design(self) -> 'bool':
        '''bool: 'CreateNewDesign' is the original name of this property.'''

        return self.wrapped.CreateNewDesign

    @create_new_design.setter
    def create_new_design(self, value: 'bool'):
        self.wrapped.CreateNewDesign = bool(value) if value else False

    @property
    def new_design_name(self) -> 'str':
        '''str: 'NewDesignName' is the original name of this property.'''

        return self.wrapped.NewDesignName

    @new_design_name.setter
    def new_design_name(self, value: 'str'):
        self.wrapped.NewDesignName = str(value) if value else ''

    @property
    def constraints(self) -> 'List[_1977.MeasuredAndFactorViewModel]':
        '''List[MeasuredAndFactorViewModel]: 'Constraints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Constraints, constructor.new(_1977.MeasuredAndFactorViewModel))
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
