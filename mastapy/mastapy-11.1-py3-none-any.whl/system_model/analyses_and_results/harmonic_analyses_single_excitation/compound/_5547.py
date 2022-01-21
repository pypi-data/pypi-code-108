'''_5547.py

BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5417
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5544
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation',)


class BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation(_5544.BevelDifferentialGearCompoundHarmonicAnalysisOfSingleExcitation):
    '''BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGearCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_5417.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5417.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5417.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation]':
        '''List[BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5417.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation))
        return value
