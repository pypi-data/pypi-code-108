'''_6188.py

InterMountableComponentConnectionCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6059
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6158
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'InterMountableComponentConnectionCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundDynamicAnalysis',)


class InterMountableComponentConnectionCompoundDynamicAnalysis(_6158.ConnectionCompoundDynamicAnalysis):
    '''InterMountableComponentConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6059.InterMountableComponentConnectionDynamicAnalysis]':
        '''List[InterMountableComponentConnectionDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6059.InterMountableComponentConnectionDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6059.InterMountableComponentConnectionDynamicAnalysis]':
        '''List[InterMountableComponentConnectionDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6059.InterMountableComponentConnectionDynamicAnalysis))
        return value
