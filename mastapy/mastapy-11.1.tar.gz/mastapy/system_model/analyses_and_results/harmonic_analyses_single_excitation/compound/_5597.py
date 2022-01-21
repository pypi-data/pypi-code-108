'''_5597.py

HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5595, _5596, _5539
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5468
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation',)


class HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation(_5539.AGMAGleasonConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation):
    '''HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
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
    def hypoid_gears_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5595.HypoidGearCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[HypoidGearCompoundHarmonicAnalysisOfSingleExcitation]: 'HypoidGearsCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5595.HypoidGearCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def hypoid_meshes_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5596.HypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[HypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation]: 'HypoidMeshesCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5596.HypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[HypoidGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[HypoidGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5468.HypoidGearSetHarmonicAnalysisOfSingleExcitation))
        return value
