'''_3709.py

PartCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3578
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'PartCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundStabilityAnalysis',)


class PartCompoundStabilityAnalysis(_7263.PartCompoundAnalysis):
    '''PartCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3578.PartStabilityAnalysis]':
        '''List[PartStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3578.PartStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3578.PartStabilityAnalysis]':
        '''List[PartStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3578.PartStabilityAnalysis))
        return value
