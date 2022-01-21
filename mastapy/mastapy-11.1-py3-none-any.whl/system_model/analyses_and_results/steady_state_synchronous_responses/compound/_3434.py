'''_3434.py

InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3302
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3404
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse',)


class InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse(_3404.ConnectionCompoundSteadyStateSynchronousResponse):
    '''InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3302.InterMountableComponentConnectionSteadyStateSynchronousResponse]':
        '''List[InterMountableComponentConnectionSteadyStateSynchronousResponse]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3302.InterMountableComponentConnectionSteadyStateSynchronousResponse))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3302.InterMountableComponentConnectionSteadyStateSynchronousResponse]':
        '''List[InterMountableComponentConnectionSteadyStateSynchronousResponse]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3302.InterMountableComponentConnectionSteadyStateSynchronousResponse))
        return value
