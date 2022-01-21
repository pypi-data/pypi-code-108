'''_3371.py

AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3237
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3394
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse',)


class AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse(_3394.ComponentCompoundSteadyStateSynchronousResponse):
    '''AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3237.AbstractShaftOrHousingSteadyStateSynchronousResponse]':
        '''List[AbstractShaftOrHousingSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3237.AbstractShaftOrHousingSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3237.AbstractShaftOrHousingSteadyStateSynchronousResponse]':
        '''List[AbstractShaftOrHousingSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3237.AbstractShaftOrHousingSteadyStateSynchronousResponse))
        return value
