'''_3694.py

HypoidGearSetCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3692, _3693, _3636
from mastapy.system_model.analyses_and_results.stability_analyses import _3562
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'HypoidGearSetCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundStabilityAnalysis',)


class HypoidGearSetCompoundStabilityAnalysis(_3636.AGMAGleasonConicalGearSetCompoundStabilityAnalysis):
    '''HypoidGearSetCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundStabilityAnalysis.TYPE'):
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
    def hypoid_gears_compound_stability_analysis(self) -> 'List[_3692.HypoidGearCompoundStabilityAnalysis]':
        '''List[HypoidGearCompoundStabilityAnalysis]: 'HypoidGearsCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundStabilityAnalysis, constructor.new(_3692.HypoidGearCompoundStabilityAnalysis))
        return value

    @property
    def hypoid_meshes_compound_stability_analysis(self) -> 'List[_3693.HypoidGearMeshCompoundStabilityAnalysis]':
        '''List[HypoidGearMeshCompoundStabilityAnalysis]: 'HypoidMeshesCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundStabilityAnalysis, constructor.new(_3693.HypoidGearMeshCompoundStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3562.HypoidGearSetStabilityAnalysis]':
        '''List[HypoidGearSetStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3562.HypoidGearSetStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3562.HypoidGearSetStabilityAnalysis]':
        '''List[HypoidGearSetStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3562.HypoidGearSetStabilityAnalysis))
        return value
