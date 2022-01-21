'''_6922.py

HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6920, _6921, _6864
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6793
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation',)


class HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation(_6864.AGMAGleasonConicalGearSetCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def hypoid_gears_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6920.HypoidGearCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[HypoidGearCompoundAdvancedTimeSteppingAnalysisForModulation]: 'HypoidGearsCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6920.HypoidGearCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def hypoid_meshes_compound_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6921.HypoidGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[HypoidGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation]: 'HypoidMeshesCompoundAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6921.HypoidGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6793.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[HypoidGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6793.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6793.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation]':
        '''List[HypoidGearSetAdvancedTimeSteppingAnalysisForModulation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6793.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation))
        return value
