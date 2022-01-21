'''_6148.py

ComponentCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6018
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6202
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'ComponentCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundDynamicAnalysis',)


class ComponentCompoundDynamicAnalysis(_6202.PartCompoundDynamicAnalysis):
    '''ComponentCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6018.ComponentDynamicAnalysis]':
        '''List[ComponentDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6018.ComponentDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6018.ComponentDynamicAnalysis]':
        '''List[ComponentDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6018.ComponentDynamicAnalysis))
        return value
