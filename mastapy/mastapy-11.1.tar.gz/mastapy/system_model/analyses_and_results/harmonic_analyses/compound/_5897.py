'''_5897.py

CVTPulleyCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5706
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5943
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'CVTPulleyCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundHarmonicAnalysis',)


class CVTPulleyCompoundHarmonicAnalysis(_5943.PulleyCompoundHarmonicAnalysis):
    '''CVTPulleyCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_5706.CVTPulleyHarmonicAnalysis]':
        '''List[CVTPulleyHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5706.CVTPulleyHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5706.CVTPulleyHarmonicAnalysis]':
        '''List[CVTPulleyHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5706.CVTPulleyHarmonicAnalysis))
        return value
