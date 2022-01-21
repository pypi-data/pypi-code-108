'''_3370.py

AbstractShaftCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3238
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3371
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'AbstractShaftCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundSteadyStateSynchronousResponse',)


class AbstractShaftCompoundSteadyStateSynchronousResponse(_3371.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse):
    '''AbstractShaftCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3238.AbstractShaftSteadyStateSynchronousResponse]':
        '''List[AbstractShaftSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3238.AbstractShaftSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3238.AbstractShaftSteadyStateSynchronousResponse]':
        '''List[AbstractShaftSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3238.AbstractShaftSteadyStateSynchronousResponse))
        return value
