'''_6238.py

SynchroniserPartCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6109
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6162
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'SynchroniserPartCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundDynamicAnalysis',)


class SynchroniserPartCompoundDynamicAnalysis(_6162.CouplingHalfCompoundDynamicAnalysis):
    '''SynchroniserPartCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6109.SynchroniserPartDynamicAnalysis]':
        '''List[SynchroniserPartDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6109.SynchroniserPartDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6109.SynchroniserPartDynamicAnalysis]':
        '''List[SynchroniserPartDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6109.SynchroniserPartDynamicAnalysis))
        return value
