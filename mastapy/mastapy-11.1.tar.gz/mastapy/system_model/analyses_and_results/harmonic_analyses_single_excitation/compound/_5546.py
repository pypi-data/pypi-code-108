'''_5546.py

BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5544, _5545, _5551
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5416
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation',)


class BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation(_5551.BevelGearSetCompoundHarmonicAnalysisOfSingleExcitation):
    '''BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def bevel_differential_gears_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5544.BevelDifferentialGearCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialGearCompoundHarmonicAnalysisOfSingleExcitation]: 'BevelDifferentialGearsCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5544.BevelDifferentialGearCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def bevel_differential_meshes_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5545.BevelDifferentialGearMeshCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialGearMeshCompoundHarmonicAnalysisOfSingleExcitation]: 'BevelDifferentialMeshesCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5545.BevelDifferentialGearMeshCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5416.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation))
        return value
