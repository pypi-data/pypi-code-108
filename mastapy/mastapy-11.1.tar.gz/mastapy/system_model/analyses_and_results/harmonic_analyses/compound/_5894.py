'''_5894.py

CouplingHalfCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5702
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5932
from mastapy._internal.python_net import python_net_import

_COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'CouplingHalfCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingHalfCompoundHarmonicAnalysis',)


class CouplingHalfCompoundHarmonicAnalysis(_5932.MountableComponentCompoundHarmonicAnalysis):
    '''CouplingHalfCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingHalfCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5702.CouplingHalfHarmonicAnalysis]':
        '''List[CouplingHalfHarmonicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5702.CouplingHalfHarmonicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5702.CouplingHalfHarmonicAnalysis]':
        '''List[CouplingHalfHarmonicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5702.CouplingHalfHarmonicAnalysis))
        return value
