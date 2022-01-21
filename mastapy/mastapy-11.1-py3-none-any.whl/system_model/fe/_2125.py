'''_2125.py

FESubstructureExportOptions
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import list_with_selected_item, enum_with_selected_value
from mastapy.utility.units_and_measurements import _1403
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.nodal_analysis.fe_export_utility import _152
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_EXPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FESubstructureExportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureExportOptions',)


class FESubstructureExportOptions(_0.APIBase):
    '''FESubstructureExportOptions

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_EXPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureExportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def include_original_fe_file(self) -> 'bool':
        '''bool: 'IncludeOriginalFEFile' is the original name of this property.'''

        return self.wrapped.IncludeOriginalFEFile

    @include_original_fe_file.setter
    def include_original_fe_file(self, value: 'bool'):
        self.wrapped.IncludeOriginalFEFile = bool(value) if value else False

    @property
    def include_rigid_coupling_nodes_and_constraints_added_by_masta(self) -> 'bool':
        '''bool: 'IncludeRigidCouplingNodesAndConstraintsAddedByMASTA' is the original name of this property.'''

        return self.wrapped.IncludeRigidCouplingNodesAndConstraintsAddedByMASTA

    @include_rigid_coupling_nodes_and_constraints_added_by_masta.setter
    def include_rigid_coupling_nodes_and_constraints_added_by_masta(self, value: 'bool'):
        self.wrapped.IncludeRigidCouplingNodesAndConstraintsAddedByMASTA = bool(value) if value else False

    @property
    def include_reduction_commands(self) -> 'bool':
        '''bool: 'IncludeReductionCommands' is the original name of this property.'''

        return self.wrapped.IncludeReductionCommands

    @include_reduction_commands.setter
    def include_reduction_commands(self, value: 'bool'):
        self.wrapped.IncludeReductionCommands = bool(value) if value else False

    @property
    def length_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'LengthUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.LengthUnit) if self.wrapped.LengthUnit is not None else None

    @length_unit.setter
    def length_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.LengthUnit = value

    @property
    def force_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'ForceUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.ForceUnit) if self.wrapped.ForceUnit is not None else None

    @force_unit.setter
    def force_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ForceUnit = value

    @property
    def fe_package(self) -> 'enum_with_selected_value.EnumWithSelectedValue_FEExportFormat':
        '''enum_with_selected_value.EnumWithSelectedValue_FEExportFormat: 'FEPackage' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.FEPackage, value) if self.wrapped.FEPackage is not None else None

    @fe_package.setter
    def fe_package(self, value: 'enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.FEPackage = value

    @property
    def include_reduced_gravity_load(self) -> 'bool':
        '''bool: 'IncludeReducedGravityLoad' is the original name of this property.'''

        return self.wrapped.IncludeReducedGravityLoad

    @include_reduced_gravity_load.setter
    def include_reduced_gravity_load(self, value: 'bool'):
        self.wrapped.IncludeReducedGravityLoad = bool(value) if value else False

    @property
    def include_reduced_thermal_expansion_force(self) -> 'bool':
        '''bool: 'IncludeReducedThermalExpansionForce' is the original name of this property.'''

        return self.wrapped.IncludeReducedThermalExpansionForce

    @include_reduced_thermal_expansion_force.setter
    def include_reduced_thermal_expansion_force(self, value: 'bool'):
        self.wrapped.IncludeReducedThermalExpansionForce = bool(value) if value else False

    @property
    def include_condensation_node_displacement_expansion(self) -> 'bool':
        '''bool: 'IncludeCondensationNodeDisplacementExpansion' is the original name of this property.'''

        return self.wrapped.IncludeCondensationNodeDisplacementExpansion

    @include_condensation_node_displacement_expansion.setter
    def include_condensation_node_displacement_expansion(self, value: 'bool'):
        self.wrapped.IncludeCondensationNodeDisplacementExpansion = bool(value) if value else False

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def export_to_file(self, file_path: 'str'):
        ''' 'ExportToFile' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.ExportToFile(file_path if file_path else '')

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
