'''_6125.py

AbstractShaftOrHousingCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _5995
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6148
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'AbstractShaftOrHousingCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundDynamicAnalysis',)


class AbstractShaftOrHousingCompoundDynamicAnalysis(_6148.ComponentCompoundDynamicAnalysis):
    '''AbstractShaftOrHousingCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5995.AbstractShaftOrHousingDynamicAnalysis]':
        '''List[AbstractShaftOrHousingDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5995.AbstractShaftOrHousingDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5995.AbstractShaftOrHousingDynamicAnalysis]':
        '''List[AbstractShaftOrHousingDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5995.AbstractShaftOrHousingDynamicAnalysis))
        return value
