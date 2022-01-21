'''_3374.py

AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3240
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3402
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse',)


class AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse(_3402.ConicalGearMeshCompoundSteadyStateSynchronousResponse):
    '''AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3240.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse]':
        '''List[AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3240.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3240.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse]':
        '''List[AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3240.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponse))
        return value
