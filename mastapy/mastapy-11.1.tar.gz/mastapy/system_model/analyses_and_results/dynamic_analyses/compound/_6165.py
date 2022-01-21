'''_6165.py

CVTPulleyCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6035
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6211
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CVTPulleyCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundDynamicAnalysis',)


class CVTPulleyCompoundDynamicAnalysis(_6211.PulleyCompoundDynamicAnalysis):
    '''CVTPulleyCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_6035.CVTPulleyDynamicAnalysis]':
        '''List[CVTPulleyDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6035.CVTPulleyDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6035.CVTPulleyDynamicAnalysis]':
        '''List[CVTPulleyDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6035.CVTPulleyDynamicAnalysis))
        return value
