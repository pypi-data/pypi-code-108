'''_5919.py

HypoidGearSetCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5917, _5918, _5861
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5751
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'HypoidGearSetCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundHarmonicAnalysis',)


class HypoidGearSetCompoundHarmonicAnalysis(_5861.AGMAGleasonConicalGearSetCompoundHarmonicAnalysis):
    '''HypoidGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundHarmonicAnalysis.TYPE'):
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
    def hypoid_gears_compound_harmonic_analysis(self) -> 'List[_5917.HypoidGearCompoundHarmonicAnalysis]':
        '''List[HypoidGearCompoundHarmonicAnalysis]: 'HypoidGearsCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundHarmonicAnalysis, constructor.new(_5917.HypoidGearCompoundHarmonicAnalysis))
        return value

    @property
    def hypoid_meshes_compound_harmonic_analysis(self) -> 'List[_5918.HypoidGearMeshCompoundHarmonicAnalysis]':
        '''List[HypoidGearMeshCompoundHarmonicAnalysis]: 'HypoidMeshesCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundHarmonicAnalysis, constructor.new(_5918.HypoidGearMeshCompoundHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5751.HypoidGearSetHarmonicAnalysis]':
        '''List[HypoidGearSetHarmonicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5751.HypoidGearSetHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5751.HypoidGearSetHarmonicAnalysis]':
        '''List[HypoidGearSetHarmonicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5751.HypoidGearSetHarmonicAnalysis))
        return value
