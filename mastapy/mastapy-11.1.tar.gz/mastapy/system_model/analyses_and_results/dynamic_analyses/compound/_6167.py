'''_6167.py

CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6037
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6147
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis',)


class CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis(_6147.CoaxialConnectionCompoundDynamicAnalysis):
    '''CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCentralBearingConnectionCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6037.CycloidalDiscCentralBearingConnectionDynamicAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6037.CycloidalDiscCentralBearingConnectionDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_6037.CycloidalDiscCentralBearingConnectionDynamicAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6037.CycloidalDiscCentralBearingConnectionDynamicAnalysis))
        return value
