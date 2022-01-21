'''_5887.py

ConicalGearCompoundHarmonicAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5696
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5913
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConicalGearCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundHarmonicAnalysis',)


class ConicalGearCompoundHarmonicAnalysis(_5913.GearCompoundHarmonicAnalysis):
    '''ConicalGearCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundHarmonicAnalysis]':
        '''List[ConicalGearCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5696.ConicalGearHarmonicAnalysis]':
        '''List[ConicalGearHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5696.ConicalGearHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5696.ConicalGearHarmonicAnalysis]':
        '''List[ConicalGearHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5696.ConicalGearHarmonicAnalysis))
        return value
