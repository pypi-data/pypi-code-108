'''_6490.py

SpiralBevelGearSetCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2284
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6488, _6489, _6407
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6361
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'SpiralBevelGearSetCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetCompoundCriticalSpeedAnalysis',)


class SpiralBevelGearSetCompoundCriticalSpeedAnalysis(_6407.BevelGearSetCompoundCriticalSpeedAnalysis):
    '''SpiralBevelGearSetCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2284.SpiralBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2284.SpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def spiral_bevel_gears_compound_critical_speed_analysis(self) -> 'List[_6488.SpiralBevelGearCompoundCriticalSpeedAnalysis]':
        '''List[SpiralBevelGearCompoundCriticalSpeedAnalysis]: 'SpiralBevelGearsCompoundCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearsCompoundCriticalSpeedAnalysis, constructor.new(_6488.SpiralBevelGearCompoundCriticalSpeedAnalysis))
        return value

    @property
    def spiral_bevel_meshes_compound_critical_speed_analysis(self) -> 'List[_6489.SpiralBevelGearMeshCompoundCriticalSpeedAnalysis]':
        '''List[SpiralBevelGearMeshCompoundCriticalSpeedAnalysis]: 'SpiralBevelMeshesCompoundCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshesCompoundCriticalSpeedAnalysis, constructor.new(_6489.SpiralBevelGearMeshCompoundCriticalSpeedAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6361.SpiralBevelGearSetCriticalSpeedAnalysis]':
        '''List[SpiralBevelGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6361.SpiralBevelGearSetCriticalSpeedAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6361.SpiralBevelGearSetCriticalSpeedAnalysis]':
        '''List[SpiralBevelGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6361.SpiralBevelGearSetCriticalSpeedAnalysis))
        return value
