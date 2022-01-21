'''_3745.py

SynchroniserPartCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3615
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3669
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'SynchroniserPartCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundStabilityAnalysis',)


class SynchroniserPartCompoundStabilityAnalysis(_3669.CouplingHalfCompoundStabilityAnalysis):
    '''SynchroniserPartCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3615.SynchroniserPartStabilityAnalysis]':
        '''List[SynchroniserPartStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3615.SynchroniserPartStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3615.SynchroniserPartStabilityAnalysis]':
        '''List[SynchroniserPartStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3615.SynchroniserPartStabilityAnalysis))
        return value
