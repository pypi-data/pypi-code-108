'''_2914.py

KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2786
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2880
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft',)


class KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft(_2880.ConicalGearCompoundSteadyStateSynchronousResponseOnAShaft):
    '''KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2786.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft]':
        '''List[KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2786.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2786.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft]':
        '''List[KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2786.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft))
        return value
