'''_6965.py

StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6963, _6964, _6876
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6836
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation',)


class StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation(_6876.BevelGearSetCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_diff_gears_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6963.StraightBevelDiffGearCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelDiffGearCompoundAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelDiffGearsCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6963.StraightBevelDiffGearCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def straight_bevel_diff_meshes_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6964.StraightBevelDiffGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelDiffGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelDiffMeshesCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6964.StraightBevelDiffGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6836.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6836.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6836.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6836.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value
