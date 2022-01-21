'''_3429.py

GearSetCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3296
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3467
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'GearSetCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundSteadyStateSynchronousResponse',)


class GearSetCompoundSteadyStateSynchronousResponse(_3467.SpecialisedAssemblyCompoundSteadyStateSynchronousResponse):
    '''GearSetCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3296.GearSetSteadyStateSynchronousResponse]':
        '''List[GearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3296.GearSetSteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3296.GearSetSteadyStateSynchronousResponse]':
        '''List[GearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3296.GearSetSteadyStateSynchronousResponse))
        return value
