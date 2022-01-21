'''_6425.py

ConnectorCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6466
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ConnectorCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundCriticalSpeedAnalysis',)


class ConnectorCompoundCriticalSpeedAnalysis(_6466.MountableComponentCompoundCriticalSpeedAnalysis):
    '''ConnectorCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6294.ConnectorCriticalSpeedAnalysis]':
        '''List[ConnectorCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6294.ConnectorCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6294.ConnectorCriticalSpeedAnalysis]':
        '''List[ConnectorCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6294.ConnectorCriticalSpeedAnalysis))
        return value
