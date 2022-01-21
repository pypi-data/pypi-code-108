'''_3755.py

WormGearSetCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3753, _3754, _3690
from mastapy.system_model.analyses_and_results.stability_analyses import _3625
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'WormGearSetCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundStabilityAnalysis',)


class WormGearSetCompoundStabilityAnalysis(_3690.GearSetCompoundStabilityAnalysis):
    '''WormGearSetCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundStabilityAnalysis.TYPE'):
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
    def worm_gears_compound_stability_analysis(self) -> 'List[_3753.WormGearCompoundStabilityAnalysis]':
        '''List[WormGearCompoundStabilityAnalysis]: 'WormGearsCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundStabilityAnalysis, constructor.new(_3753.WormGearCompoundStabilityAnalysis))
        return value

    @property
    def worm_meshes_compound_stability_analysis(self) -> 'List[_3754.WormGearMeshCompoundStabilityAnalysis]':
        '''List[WormGearMeshCompoundStabilityAnalysis]: 'WormMeshesCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundStabilityAnalysis, constructor.new(_3754.WormGearMeshCompoundStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3625.WormGearSetStabilityAnalysis]':
        '''List[WormGearSetStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3625.WormGearSetStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3625.WormGearSetStabilityAnalysis]':
        '''List[WormGearSetStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3625.WormGearSetStabilityAnalysis))
        return value
