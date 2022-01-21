'''_3109.py

AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _2978
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed.compound import _3132
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed.Compound', 'AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed',)


class AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed(_3132.ComponentCompoundSteadyStateSynchronousResponseAtASpeed):
    '''AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2978.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed]':
        '''List[AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2978.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2978.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed]':
        '''List[AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2978.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed))
        return value
