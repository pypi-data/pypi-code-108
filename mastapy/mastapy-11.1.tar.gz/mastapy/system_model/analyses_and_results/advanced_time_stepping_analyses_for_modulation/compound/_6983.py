'''_6983.py

WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6981, _6982, _6918
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6854
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation',)


class WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation(_6918.GearSetCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def worm_gears_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6981.WormGearCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearCompoundAdvancedTimeSteppingAnalysisForModulation]: 'WormGearsCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6981.WormGearCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def worm_meshes_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6982.WormGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]: 'WormMeshesCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6982.WormGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6854.WormGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6854.WormGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6854.WormGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6854.WormGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value
