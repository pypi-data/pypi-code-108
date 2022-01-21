'''_6161.py

CouplingConnectionCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6030
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6188
from mastapy._internal.python_net import python_net_import

_COUPLING_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CouplingConnectionCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingConnectionCompoundDynamicAnalysis',)


class CouplingConnectionCompoundDynamicAnalysis(_6188.InterMountableComponentConnectionCompoundDynamicAnalysis):
    '''CouplingConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingConnectionCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6030.CouplingConnectionDynamicAnalysis]':
        '''List[CouplingConnectionDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6030.CouplingConnectionDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6030.CouplingConnectionDynamicAnalysis]':
        '''List[CouplingConnectionDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6030.CouplingConnectionDynamicAnalysis))
        return value
