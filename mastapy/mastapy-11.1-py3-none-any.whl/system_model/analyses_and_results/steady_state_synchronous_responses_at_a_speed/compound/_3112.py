'''_3112.py

AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _2981
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed.compound import _3140
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed.Compound', 'AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed',)


class AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed(_3140.ConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed):
    '''AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2981.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed]':
        '''List[AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2981.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2981.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed]':
        '''List[AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2981.AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseAtASpeed))
        return value
