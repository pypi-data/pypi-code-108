'''_3143.py

ConnectorCompoundSteadyStateSynchronousResponseAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _3013
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed.compound import _3184
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed.Compound', 'ConnectorCompoundSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundSteadyStateSynchronousResponseAtASpeed',)


class ConnectorCompoundSteadyStateSynchronousResponseAtASpeed(_3184.MountableComponentCompoundSteadyStateSynchronousResponseAtASpeed):
    '''ConnectorCompoundSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3013.ConnectorSteadyStateSynchronousResponseAtASpeed]':
        '''List[ConnectorSteadyStateSynchronousResponseAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3013.ConnectorSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3013.ConnectorSteadyStateSynchronousResponseAtASpeed]':
        '''List[ConnectorSteadyStateSynchronousResponseAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3013.ConnectorSteadyStateSynchronousResponseAtASpeed))
        return value
