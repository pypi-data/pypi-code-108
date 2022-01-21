'''_1979.py

OptimizationStep
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.optimization import _1978
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OPTIMIZATION_STEP = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'OptimizationStep')


__docformat__ = 'restructuredtext en'
__all__ = ('OptimizationStep',)


class OptimizationStep(_0.APIBase):
    '''OptimizationStep

    This is a mastapy class.
    '''

    TYPE = _OPTIMIZATION_STEP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptimizationStep.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def target_edge_stress_factor(self) -> 'float':
        '''float: 'TargetEdgeStressFactor' is the original name of this property.'''

        return self.wrapped.TargetEdgeStressFactor

    @target_edge_stress_factor.setter
    def target_edge_stress_factor(self, value: 'float'):
        self.wrapped.TargetEdgeStressFactor = float(value) if value else 0.0

    @property
    def tolerance(self) -> 'float':
        '''float: 'Tolerance' is the original name of this property.'''

        return self.wrapped.Tolerance

    @tolerance.setter
    def tolerance(self, value: 'float'):
        self.wrapped.Tolerance = float(value) if value else 0.0

    @property
    def optimisation_target(self) -> '_1978.MicroGeometryOptimisationTarget':
        '''MicroGeometryOptimisationTarget: 'OptimisationTarget' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.OptimisationTarget)
        return constructor.new(_1978.MicroGeometryOptimisationTarget)(value) if value is not None else None

    @optimisation_target.setter
    def optimisation_target(self, value: '_1978.MicroGeometryOptimisationTarget'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.OptimisationTarget = value

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
