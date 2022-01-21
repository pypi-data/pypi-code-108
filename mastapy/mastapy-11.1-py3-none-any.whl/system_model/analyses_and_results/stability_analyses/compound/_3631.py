'''_3631.py

AbstractShaftCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3500
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3632
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'AbstractShaftCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundStabilityAnalysis',)


class AbstractShaftCompoundStabilityAnalysis(_3632.AbstractShaftOrHousingCompoundStabilityAnalysis):
    '''AbstractShaftCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3500.AbstractShaftStabilityAnalysis]':
        '''List[AbstractShaftStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3500.AbstractShaftStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3500.AbstractShaftStabilityAnalysis]':
        '''List[AbstractShaftStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3500.AbstractShaftStabilityAnalysis))
        return value
