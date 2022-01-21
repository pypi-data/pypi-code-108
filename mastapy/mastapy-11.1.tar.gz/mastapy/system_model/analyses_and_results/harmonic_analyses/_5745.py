'''_5745.py

HarmonicAnalysisFEExportOptions
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item, enum_with_selected_value
from mastapy.utility.units_and_measurements import _1403
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis.fe_export_utility import _152
from mastapy.system_model.analyses_and_results.harmonic_analyses import (
    _5746, _5788, _5734, _5744
)
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6790
from mastapy._internal.cast_exception import CastException
from mastapy.nodal_analysis.dev_tools_analyses import _154
from mastapy.system_model.analyses_and_results import _2394
from mastapy.system_model.part_model import _2194
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_FE_EXPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'HarmonicAnalysisFEExportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisFEExportOptions',)


class HarmonicAnalysisFEExportOptions(_5744.HarmonicAnalysisExportOptions['_2394.IHaveFEPartHarmonicAnalysisResults', '_2194.FEPart']):
    '''HarmonicAnalysisFEExportOptions

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_FE_EXPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisFEExportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def distance_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'DistanceUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.DistanceUnit) if self.wrapped.DistanceUnit is not None else None

    @distance_unit.setter
    def distance_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.DistanceUnit = value

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
    def export_full_mesh(self) -> 'bool':
        '''bool: 'ExportFullMesh' is the original name of this property.'''

        return self.wrapped.ExportFullMesh

    @export_full_mesh.setter
    def export_full_mesh(self, value: 'bool'):
        self.wrapped.ExportFullMesh = bool(value) if value else False

    @property
    def complex_number_output_option(self) -> 'enum_with_selected_value.EnumWithSelectedValue_HarmonicAnalysisFEExportOptions_ComplexNumberOutput':
        '''enum_with_selected_value.EnumWithSelectedValue_HarmonicAnalysisFEExportOptions_ComplexNumberOutput: 'ComplexNumberOutputOption' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_HarmonicAnalysisFEExportOptions_ComplexNumberOutput.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ComplexNumberOutputOption, value) if self.wrapped.ComplexNumberOutputOption is not None else None

    @complex_number_output_option.setter
    def complex_number_output_option(self, value: 'enum_with_selected_value.EnumWithSelectedValue_HarmonicAnalysisFEExportOptions_ComplexNumberOutput.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_HarmonicAnalysisFEExportOptions_ComplexNumberOutput.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ComplexNumberOutputOption = value

    @property
    def include_original_fe_file(self) -> 'bool':
        '''bool: 'IncludeOriginalFEFile' is the original name of this property.'''

        return self.wrapped.IncludeOriginalFEFile

    @include_original_fe_file.setter
    def include_original_fe_file(self, value: 'bool'):
        self.wrapped.IncludeOriginalFEFile = bool(value) if value else False

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
    def include_all_shafts(self) -> 'bool':
        '''bool: 'IncludeAllShafts' is the original name of this property.'''

        return self.wrapped.IncludeAllShafts

    @include_all_shafts.setter
    def include_all_shafts(self, value: 'bool'):
        self.wrapped.IncludeAllShafts = bool(value) if value else False

    @property
    def include_all_fe_models(self) -> 'bool':
        '''bool: 'IncludeAllFEModels' is the original name of this property.'''

        return self.wrapped.IncludeAllFEModels

    @include_all_fe_models.setter
    def include_all_fe_models(self, value: 'bool'):
        self.wrapped.IncludeAllFEModels = bool(value) if value else False

    @property
    def include_rigid_couplings_and_nodes_added_by_masta(self) -> 'bool':
        '''bool: 'IncludeRigidCouplingsAndNodesAddedByMASTA' is the original name of this property.'''

        return self.wrapped.IncludeRigidCouplingsAndNodesAddedByMASTA

    @include_rigid_couplings_and_nodes_added_by_masta.setter
    def include_rigid_couplings_and_nodes_added_by_masta(self, value: 'bool'):
        self.wrapped.IncludeRigidCouplingsAndNodesAddedByMASTA = bool(value) if value else False

    @property
    def use_single_speed(self) -> 'bool':
        '''bool: 'UseSingleSpeed' is the original name of this property.'''

        return self.wrapped.UseSingleSpeed

    @use_single_speed.setter
    def use_single_speed(self, value: 'bool'):
        self.wrapped.UseSingleSpeed = bool(value) if value else False

    @property
    def reference_speed(self) -> 'float':
        '''float: 'ReferenceSpeed' is the original name of this property.'''

        return self.wrapped.ReferenceSpeed

    @reference_speed.setter
    def reference_speed(self, value: 'float'):
        self.wrapped.ReferenceSpeed = float(value) if value else 0.0

    @property
    def combine_excitations_of_same_order(self) -> 'bool':
        '''bool: 'CombineExcitationsOfSameOrder' is the original name of this property.'''

        return self.wrapped.CombineExcitationsOfSameOrder

    @combine_excitations_of_same_order.setter
    def combine_excitations_of_same_order(self, value: 'bool'):
        self.wrapped.CombineExcitationsOfSameOrder = bool(value) if value else False

    @property
    def combine_excitations_from_different_parts(self) -> 'bool':
        '''bool: 'CombineExcitationsFromDifferentParts' is the original name of this property.'''

        return self.wrapped.CombineExcitationsFromDifferentParts

    @combine_excitations_from_different_parts.setter
    def combine_excitations_from_different_parts(self, value: 'bool'):
        self.wrapped.CombineExcitationsFromDifferentParts = bool(value) if value else False

    @property
    def status_message_for_export(self) -> 'str':
        '''str: 'StatusMessageForExport' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StatusMessageForExport

    @property
    def analysis_options(self) -> '_5746.HarmonicAnalysisOptions':
        '''HarmonicAnalysisOptions: 'AnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5746.HarmonicAnalysisOptions.TYPE not in self.wrapped.AnalysisOptions.__class__.__mro__:
            raise CastException('Failed to cast analysis_options to HarmonicAnalysisOptions. Expected: {}.'.format(self.wrapped.AnalysisOptions.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AnalysisOptions.__class__)(self.wrapped.AnalysisOptions) if self.wrapped.AnalysisOptions is not None else None

    @property
    def reference_speed_options(self) -> '_5788.SpeedOptionsForHarmonicAnalysisResults':
        '''SpeedOptionsForHarmonicAnalysisResults: 'ReferenceSpeedOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5788.SpeedOptionsForHarmonicAnalysisResults)(self.wrapped.ReferenceSpeedOptions) if self.wrapped.ReferenceSpeedOptions is not None else None

    @property
    def frequency_options(self) -> '_5734.FrequencyOptionsForHarmonicAnalysisResults':
        '''FrequencyOptionsForHarmonicAnalysisResults: 'FrequencyOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5734.FrequencyOptionsForHarmonicAnalysisResults)(self.wrapped.FrequencyOptions) if self.wrapped.FrequencyOptions is not None else None

    @property
    def eigenvalue_options(self) -> '_154.EigenvalueOptions':
        '''EigenvalueOptions: 'EigenvalueOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_154.EigenvalueOptions)(self.wrapped.EigenvalueOptions) if self.wrapped.EigenvalueOptions is not None else None

    def export_to_folder(self, folder_path: 'str') -> 'List[str]':
        ''' 'ExportToFolder' is the original name of this method.

        Args:
            folder_path (str)

        Returns:
            List[str]
        '''

        folder_path = str(folder_path)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.ExportToFolder(folder_path if folder_path else ''), str)
