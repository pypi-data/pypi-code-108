'''_3491.py

VirtualComponentCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3362
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3446
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'VirtualComponentCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundSteadyStateSynchronousResponse',)


class VirtualComponentCompoundSteadyStateSynchronousResponse(_3446.MountableComponentCompoundSteadyStateSynchronousResponse):
    '''VirtualComponentCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3362.VirtualComponentSteadyStateSynchronousResponse]':
        '''List[VirtualComponentSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3362.VirtualComponentSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3362.VirtualComponentSteadyStateSynchronousResponse]':
        '''List[VirtualComponentSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3362.VirtualComponentSteadyStateSynchronousResponse))
        return value
