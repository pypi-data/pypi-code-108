'''_201.py

CMSOptions
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.math_utility import _1301
from mastapy.nodal_analysis.dev_tools_analyses import _154
from mastapy.fe_tools.vfx_tools import _1182
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CMS_OPTIONS = python_net_import('SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis', 'CMSOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('CMSOptions',)


class CMSOptions(_0.APIBase):
    '''CMSOptions

    This is a mastapy class.
    '''

    TYPE = _CMS_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CMSOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mode_options_description(self) -> 'str':
        '''str: 'ModeOptionsDescription' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModeOptionsDescription

    @property
    def store_condensation_node_displacement_expansion(self) -> 'bool':
        '''bool: 'StoreCondensationNodeDisplacementExpansion' is the original name of this property.'''

        return self.wrapped.StoreCondensationNodeDisplacementExpansion

    @store_condensation_node_displacement_expansion.setter
    def store_condensation_node_displacement_expansion(self, value: 'bool'):
        self.wrapped.StoreCondensationNodeDisplacementExpansion = bool(value) if value else False

    @property
    def precision_when_saving_expansion_vectors(self) -> '_1301.DataPrecision':
        '''DataPrecision: 'PrecisionWhenSavingExpansionVectors' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PrecisionWhenSavingExpansionVectors)
        return constructor.new(_1301.DataPrecision)(value) if value is not None else None

    @precision_when_saving_expansion_vectors.setter
    def precision_when_saving_expansion_vectors(self, value: '_1301.DataPrecision'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PrecisionWhenSavingExpansionVectors = value

    @property
    def calculate_reduced_gravity_load(self) -> 'bool':
        '''bool: 'CalculateReducedGravityLoad' is the original name of this property.'''

        return self.wrapped.CalculateReducedGravityLoad

    @calculate_reduced_gravity_load.setter
    def calculate_reduced_gravity_load(self, value: 'bool'):
        self.wrapped.CalculateReducedGravityLoad = bool(value) if value else False

    @property
    def calculate_reduced_thermal_expansion_force(self) -> 'bool':
        '''bool: 'CalculateReducedThermalExpansionForce' is the original name of this property.'''

        return self.wrapped.CalculateReducedThermalExpansionForce

    @calculate_reduced_thermal_expansion_force.setter
    def calculate_reduced_thermal_expansion_force(self, value: 'bool'):
        self.wrapped.CalculateReducedThermalExpansionForce = bool(value) if value else False

    @property
    def internal_mode_options(self) -> '_154.EigenvalueOptions':
        '''EigenvalueOptions: 'InternalModeOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_154.EigenvalueOptions)(self.wrapped.InternalModeOptions) if self.wrapped.InternalModeOptions is not None else None

    @property
    def solver_options(self) -> '_1182.ProSolveOptions':
        '''ProSolveOptions: 'SolverOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1182.ProSolveOptions)(self.wrapped.SolverOptions) if self.wrapped.SolverOptions is not None else None

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
