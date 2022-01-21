'''_5911.py

FEPartCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5732
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5857
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'FEPartCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundHarmonicAnalysis',)


class FEPartCompoundHarmonicAnalysis(_5857.AbstractShaftOrHousingCompoundHarmonicAnalysis):
    '''FEPartCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5732.FEPartHarmonicAnalysis]':
        '''List[FEPartHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5732.FEPartHarmonicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundHarmonicAnalysis]':
        '''List[FEPartCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5732.FEPartHarmonicAnalysis]':
        '''List[FEPartHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5732.FEPartHarmonicAnalysis))
        return value
