'''_5859.py

AGMAGleasonConicalGearCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5667
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5887
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'AGMAGleasonConicalGearCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundHarmonicAnalysis',)


class AGMAGleasonConicalGearCompoundHarmonicAnalysis(_5887.ConicalGearCompoundHarmonicAnalysis):
    '''AGMAGleasonConicalGearCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5667.AGMAGleasonConicalGearHarmonicAnalysis]':
        '''List[AGMAGleasonConicalGearHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5667.AGMAGleasonConicalGearHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5667.AGMAGleasonConicalGearHarmonicAnalysis]':
        '''List[AGMAGleasonConicalGearHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5667.AGMAGleasonConicalGearHarmonicAnalysis))
        return value
