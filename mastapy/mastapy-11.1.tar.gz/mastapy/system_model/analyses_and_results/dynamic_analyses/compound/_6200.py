'''_6200.py

MountableComponentCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6071
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6148
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'MountableComponentCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundDynamicAnalysis',)


class MountableComponentCompoundDynamicAnalysis(_6148.ComponentCompoundDynamicAnalysis):
    '''MountableComponentCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6071.MountableComponentDynamicAnalysis]':
        '''List[MountableComponentDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6071.MountableComponentDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6071.MountableComponentDynamicAnalysis]':
        '''List[MountableComponentDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6071.MountableComponentDynamicAnalysis))
        return value
