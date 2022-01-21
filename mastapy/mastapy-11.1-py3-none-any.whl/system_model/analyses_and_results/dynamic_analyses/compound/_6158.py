'''_6158.py

ConnectionCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6028
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7256
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'ConnectionCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundDynamicAnalysis',)


class ConnectionCompoundDynamicAnalysis(_7256.ConnectionCompoundAnalysis):
    '''ConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6028.ConnectionDynamicAnalysis]':
        '''List[ConnectionDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6028.ConnectionDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6028.ConnectionDynamicAnalysis]':
        '''List[ConnectionDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6028.ConnectionDynamicAnalysis))
        return value
