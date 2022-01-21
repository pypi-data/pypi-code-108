'''_5640.py

StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5638, _5639, _5551
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5511
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation',)


class StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation(_5551.BevelGearSetCompoundHarmonicAnalysisOfSingleExcitation):
    '''StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_diff_gears_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5638.StraightBevelDiffGearCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearCompoundHarmonicAnalysisOfSingleExcitation]: 'StraightBevelDiffGearsCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5638.StraightBevelDiffGearCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def straight_bevel_diff_meshes_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5639.StraightBevelDiffGearMeshCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearMeshCompoundHarmonicAnalysisOfSingleExcitation]: 'StraightBevelDiffMeshesCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5639.StraightBevelDiffGearMeshCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5511.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation))
        return value
