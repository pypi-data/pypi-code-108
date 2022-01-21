'''_6163.py

CVTBeltConnectionCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6033
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6132
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CVTBeltConnectionCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionCompoundDynamicAnalysis',)


class CVTBeltConnectionCompoundDynamicAnalysis(_6132.BeltConnectionCompoundDynamicAnalysis):
    '''CVTBeltConnectionCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6033.CVTBeltConnectionDynamicAnalysis]':
        '''List[CVTBeltConnectionDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6033.CVTBeltConnectionDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_6033.CVTBeltConnectionDynamicAnalysis]':
        '''List[CVTBeltConnectionDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6033.CVTBeltConnectionDynamicAnalysis))
        return value
