'''_6454.py

InterMountableComponentConnectionCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6325
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6424
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'InterMountableComponentConnectionCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundCriticalSpeedAnalysis',)


class InterMountableComponentConnectionCompoundCriticalSpeedAnalysis(_6424.ConnectionCompoundCriticalSpeedAnalysis):
    '''InterMountableComponentConnectionCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6325.InterMountableComponentConnectionCriticalSpeedAnalysis]':
        '''List[InterMountableComponentConnectionCriticalSpeedAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6325.InterMountableComponentConnectionCriticalSpeedAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6325.InterMountableComponentConnectionCriticalSpeedAnalysis]':
        '''List[InterMountableComponentConnectionCriticalSpeedAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6325.InterMountableComponentConnectionCriticalSpeedAnalysis))
        return value
