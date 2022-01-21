'''_5886.py

ConceptGearSetCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2262
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5884, _5885, _5915
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5695
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConceptGearSetCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetCompoundHarmonicAnalysis',)


class ConceptGearSetCompoundHarmonicAnalysis(_5915.GearSetCompoundHarmonicAnalysis):
    '''ConceptGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def concept_gears_compound_harmonic_analysis(self) -> 'List[_5884.ConceptGearCompoundHarmonicAnalysis]':
        '''List[ConceptGearCompoundHarmonicAnalysis]: 'ConceptGearsCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsCompoundHarmonicAnalysis, constructor.new(_5884.ConceptGearCompoundHarmonicAnalysis))
        return value

    @property
    def concept_meshes_compound_harmonic_analysis(self) -> 'List[_5885.ConceptGearMeshCompoundHarmonicAnalysis]':
        '''List[ConceptGearMeshCompoundHarmonicAnalysis]: 'ConceptMeshesCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesCompoundHarmonicAnalysis, constructor.new(_5885.ConceptGearMeshCompoundHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5695.ConceptGearSetHarmonicAnalysis]':
        '''List[ConceptGearSetHarmonicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5695.ConceptGearSetHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5695.ConceptGearSetHarmonicAnalysis]':
        '''List[ConceptGearSetHarmonicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5695.ConceptGearSetHarmonicAnalysis))
        return value
