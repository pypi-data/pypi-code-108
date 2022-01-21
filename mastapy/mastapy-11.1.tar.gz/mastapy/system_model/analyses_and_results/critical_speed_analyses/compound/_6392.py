'''_6392.py

AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6261
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6424
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis',)


class AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis(_6424.ConnectionCompoundCriticalSpeedAnalysis):
    '''AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6261.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]':
        '''List[AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6261.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6261.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]':
        '''List[AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6261.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis))
        return value
