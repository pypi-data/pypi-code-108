'''_2151.py

SystemDeflectionFEExportOptions
'''


from typing import List, Optional

from mastapy._internal.implicit import enum_with_selected_value, list_with_selected_item
from mastapy.nodal_analysis.fe_export_utility import _151, _152
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.utility.units_and_measurements import _1403
from mastapy.system_model.fe import _2146, _2145
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SYSTEM_DEFLECTION_FE_EXPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'SystemDeflectionFEExportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('SystemDeflectionFEExportOptions',)


class SystemDeflectionFEExportOptions(_0.APIBase):
    '''SystemDeflectionFEExportOptions

    This is a mastapy class.
    '''

    TYPE = _SYSTEM_DEFLECTION_FE_EXPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SystemDeflectionFEExportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def default_type_of_result_to_export(self) -> 'enum_with_selected_value.EnumWithSelectedValue_BoundaryConditionType':
        '''enum_with_selected_value.EnumWithSelectedValue_BoundaryConditionType: 'DefaultTypeOfResultToExport' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_BoundaryConditionType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultTypeOfResultToExport, value) if self.wrapped.DefaultTypeOfResultToExport is not None else None

    @default_type_of_result_to_export.setter
    def default_type_of_result_to_export(self, value: 'enum_with_selected_value.EnumWithSelectedValue_BoundaryConditionType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_BoundaryConditionType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultTypeOfResultToExport = value

    @property
    def include_rigid_coupling_nodes_and_constraints_added_by_masta(self) -> 'bool':
        '''bool: 'IncludeRigidCouplingNodesAndConstraintsAddedByMASTA' is the original name of this property.'''

        return self.wrapped.IncludeRigidCouplingNodesAndConstraintsAddedByMASTA

    @include_rigid_coupling_nodes_and_constraints_added_by_masta.setter
    def include_rigid_coupling_nodes_and_constraints_added_by_masta(self, value: 'bool'):
        self.wrapped.IncludeRigidCouplingNodesAndConstraintsAddedByMASTA = bool(value) if value else False

    @property
    def base_couplings_on_alternative_fe_mesh(self) -> 'bool':
        '''bool: 'BaseCouplingsOnAlternativeFEMesh' is the original name of this property.'''

        return self.wrapped.BaseCouplingsOnAlternativeFEMesh

    @base_couplings_on_alternative_fe_mesh.setter
    def base_couplings_on_alternative_fe_mesh(self, value: 'bool'):
        self.wrapped.BaseCouplingsOnAlternativeFEMesh = bool(value) if value else False

    @property
    def alternative_fe_mesh_file(self) -> 'str':
        '''str: 'AlternativeFEMeshFile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AlternativeFEMeshFile

    @property
    def use_rigid_coupling_types_from_fe_substructure_for_exported_couplings(self) -> 'bool':
        '''bool: 'UseRigidCouplingTypesFromFESubstructureForExportedCouplings' is the original name of this property.'''

        return self.wrapped.UseRigidCouplingTypesFromFESubstructureForExportedCouplings

    @use_rigid_coupling_types_from_fe_substructure_for_exported_couplings.setter
    def use_rigid_coupling_types_from_fe_substructure_for_exported_couplings(self, value: 'bool'):
        self.wrapped.UseRigidCouplingTypesFromFESubstructureForExportedCouplings = bool(value) if value else False

    @property
    def include_an_fe_mesh(self) -> 'bool':
        '''bool: 'IncludeAnFEMesh' is the original name of this property.'''

        return self.wrapped.IncludeAnFEMesh

    @include_an_fe_mesh.setter
    def include_an_fe_mesh(self, value: 'bool'):
        self.wrapped.IncludeAnFEMesh = bool(value) if value else False

    @property
    def path_of_fe_mesh_file_to_be_included(self) -> 'str':
        '''str: 'PathOfFEMeshFileToBeIncluded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PathOfFEMeshFileToBeIncluded

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
    def fe_export_format(self) -> 'enum_with_selected_value.EnumWithSelectedValue_FEExportFormat':
        '''enum_with_selected_value.EnumWithSelectedValue_FEExportFormat: 'FEExportFormat' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.FEExportFormat, value) if self.wrapped.FEExportFormat is not None else None

    @fe_export_format.setter
    def fe_export_format(self, value: 'enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_FEExportFormat.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.FEExportFormat = value

    @property
    def file_type(self) -> 'SystemDeflectionFEExportOptions.ExportType':
        '''ExportType: 'FileType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FileType)
        return constructor.new(SystemDeflectionFEExportOptions.ExportType)(value) if value is not None else None

    @file_type.setter
    def file_type(self, value: 'SystemDeflectionFEExportOptions.ExportType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FileType = value

    @property
    def nodes(self) -> 'List[_2146.PerNodeExportOptions]':
        '''List[PerNodeExportOptions]: 'Nodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Nodes, constructor.new(_2146.PerNodeExportOptions))
        return value

    @property
    def links(self) -> 'List[_2145.PerLinkExportOptions]':
        '''List[PerLinkExportOptions]: 'Links' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Links, constructor.new(_2145.PerLinkExportOptions))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def set_alternative_fe_mesh_file(self, file_path: 'str', format_: '_152.FEExportFormat', length_scale: Optional['float'] = 1.0, force_scale: Optional['float'] = 1.0):
        ''' 'SetAlternativeFEMeshFile' is the original name of this method.

        Args:
            file_path (str)
            format_ (mastapy.nodal_analysis.fe_export_utility.FEExportFormat)
            length_scale (float, optional)
            force_scale (float, optional)
        '''

        file_path = str(file_path)
        format_ = conversion.mp_to_pn_enum(format_)
        length_scale = float(length_scale)
        force_scale = float(force_scale)
        self.wrapped.SetAlternativeFEMeshFile(file_path if file_path else '', format_, length_scale if length_scale else 0.0, force_scale if force_scale else 0.0)

    def set_fe_mesh_file_to_include(self, file_path: 'str', format_: '_152.FEExportFormat', length_scale: Optional['float'] = 1.0, force_scale: Optional['float'] = 1.0):
        ''' 'SetFEMeshFileToInclude' is the original name of this method.

        Args:
            file_path (str)
            format_ (mastapy.nodal_analysis.fe_export_utility.FEExportFormat)
            length_scale (float, optional)
            force_scale (float, optional)
        '''

        file_path = str(file_path)
        format_ = conversion.mp_to_pn_enum(format_)
        length_scale = float(length_scale)
        force_scale = float(force_scale)
        self.wrapped.SetFEMeshFileToInclude(file_path if file_path else '', format_, length_scale if length_scale else 0.0, force_scale if force_scale else 0.0)

    def export_to_op2_file(self, file_path: 'str'):
        ''' 'ExportToOP2File' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.ExportToOP2File(file_path if file_path else '')

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
