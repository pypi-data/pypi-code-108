'''_5575.py

CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5445
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5621
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation',)


class CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation(_5621.PulleyCompoundHarmonicAnalysisOfSingleExcitation):
    '''CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_5445.CVTPulleyHarmonicAnalysisOfSingleExcitation]':
        '''List[CVTPulleyHarmonicAnalysisOfSingleExcitation]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5445.CVTPulleyHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5445.CVTPulleyHarmonicAnalysisOfSingleExcitation]':
        '''List[CVTPulleyHarmonicAnalysisOfSingleExcitation]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5445.CVTPulleyHarmonicAnalysisOfSingleExcitation))
        return value
