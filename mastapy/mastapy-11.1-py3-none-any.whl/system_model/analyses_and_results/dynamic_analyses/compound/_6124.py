'''_6124.py

AbstractShaftCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _5994
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6125
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'AbstractShaftCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundDynamicAnalysis',)


class AbstractShaftCompoundDynamicAnalysis(_6125.AbstractShaftOrHousingCompoundDynamicAnalysis):
    '''AbstractShaftCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5994.AbstractShaftDynamicAnalysis]':
        '''List[AbstractShaftDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5994.AbstractShaftDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5994.AbstractShaftDynamicAnalysis]':
        '''List[AbstractShaftDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5994.AbstractShaftDynamicAnalysis))
        return value
