'''_3758.py

ZerolBevelGearSetCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3756, _3757, _3648
from mastapy.system_model.analyses_and_results.stability_analyses import _3628
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ZerolBevelGearSetCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetCompoundStabilityAnalysis',)


class ZerolBevelGearSetCompoundStabilityAnalysis(_3648.BevelGearSetCompoundStabilityAnalysis):
    '''ZerolBevelGearSetCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def zerol_bevel_gears_compound_stability_analysis(self) -> 'List[_3756.ZerolBevelGearCompoundStabilityAnalysis]':
        '''List[ZerolBevelGearCompoundStabilityAnalysis]: 'ZerolBevelGearsCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearsCompoundStabilityAnalysis, constructor.new(_3756.ZerolBevelGearCompoundStabilityAnalysis))
        return value

    @property
    def zerol_bevel_meshes_compound_stability_analysis(self) -> 'List[_3757.ZerolBevelGearMeshCompoundStabilityAnalysis]':
        '''List[ZerolBevelGearMeshCompoundStabilityAnalysis]: 'ZerolBevelMeshesCompoundStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshesCompoundStabilityAnalysis, constructor.new(_3757.ZerolBevelGearMeshCompoundStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3628.ZerolBevelGearSetStabilityAnalysis]':
        '''List[ZerolBevelGearSetStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3628.ZerolBevelGearSetStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3628.ZerolBevelGearSetStabilityAnalysis]':
        '''List[ZerolBevelGearSetStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3628.ZerolBevelGearSetStabilityAnalysis))
        return value
