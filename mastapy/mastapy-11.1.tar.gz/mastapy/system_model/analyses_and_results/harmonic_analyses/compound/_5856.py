'''_5856.py

AbstractShaftCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5664
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5857
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'AbstractShaftCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundHarmonicAnalysis',)


class AbstractShaftCompoundHarmonicAnalysis(_5857.AbstractShaftOrHousingCompoundHarmonicAnalysis):
    '''AbstractShaftCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5664.AbstractShaftHarmonicAnalysis]':
        '''List[AbstractShaftHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5664.AbstractShaftHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5664.AbstractShaftHarmonicAnalysis]':
        '''List[AbstractShaftHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5664.AbstractShaftHarmonicAnalysis))
        return value
