'''_2881.py

ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2750
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2907
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft',)


class ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft(_2907.GearMeshCompoundSteadyStateSynchronousResponseOnAShaft):
    '''ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_2750.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConicalGearMeshSteadyStateSynchronousResponseOnAShaft]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2750.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2750.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConicalGearMeshSteadyStateSynchronousResponseOnAShaft]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2750.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft))
        return value
