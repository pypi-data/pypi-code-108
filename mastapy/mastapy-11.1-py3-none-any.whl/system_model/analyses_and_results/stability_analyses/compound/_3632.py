'''_3632.py

AbstractShaftOrHousingCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3499
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3655
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'AbstractShaftOrHousingCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundStabilityAnalysis',)


class AbstractShaftOrHousingCompoundStabilityAnalysis(_3655.ComponentCompoundStabilityAnalysis):
    '''AbstractShaftOrHousingCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3499.AbstractShaftOrHousingStabilityAnalysis]':
        '''List[AbstractShaftOrHousingStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3499.AbstractShaftOrHousingStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3499.AbstractShaftOrHousingStabilityAnalysis]':
        '''List[AbstractShaftOrHousingStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3499.AbstractShaftOrHousingStabilityAnalysis))
        return value
