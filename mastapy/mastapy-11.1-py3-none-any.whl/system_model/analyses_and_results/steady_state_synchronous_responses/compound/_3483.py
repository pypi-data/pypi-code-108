'''_3483.py

SynchroniserHalfCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2344
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3353
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3484
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'SynchroniserHalfCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalfCompoundSteadyStateSynchronousResponse',)


class SynchroniserHalfCompoundSteadyStateSynchronousResponse(_3484.SynchroniserPartCompoundSteadyStateSynchronousResponse):
    '''SynchroniserHalfCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalfCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3353.SynchroniserHalfSteadyStateSynchronousResponse]':
        '''List[SynchroniserHalfSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3353.SynchroniserHalfSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3353.SynchroniserHalfSteadyStateSynchronousResponse]':
        '''List[SynchroniserHalfSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3353.SynchroniserHalfSteadyStateSynchronousResponse))
        return value
