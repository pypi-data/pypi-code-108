'''_6202.py

PartCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6073
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'PartCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundDynamicAnalysis',)


class PartCompoundDynamicAnalysis(_7263.PartCompoundAnalysis):
    '''PartCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6073.PartDynamicAnalysis]':
        '''List[PartDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6073.PartDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6073.PartDynamicAnalysis]':
        '''List[PartDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6073.PartDynamicAnalysis))
        return value
