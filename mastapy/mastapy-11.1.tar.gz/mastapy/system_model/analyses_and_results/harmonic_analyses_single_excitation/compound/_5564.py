'''_5564.py

ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2262
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5562, _5563, _5593
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5434
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation',)


class ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation(_5593.GearSetCompoundHarmonicAnalysisOfSingleExcitation):
    '''ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
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
    def concept_gears_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5562.ConceptGearCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptGearCompoundHarmonicAnalysisOfSingleExcitation]: 'ConceptGearsCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5562.ConceptGearCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def concept_meshes_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5563.ConceptGearMeshCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptGearMeshCompoundHarmonicAnalysisOfSingleExcitation]: 'ConceptMeshesCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5563.ConceptGearMeshCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[ConceptGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5434.ConceptGearSetHarmonicAnalysisOfSingleExcitation))
        return value
