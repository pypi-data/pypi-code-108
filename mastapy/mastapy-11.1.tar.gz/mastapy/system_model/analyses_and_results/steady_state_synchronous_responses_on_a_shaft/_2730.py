'''_2730.py

BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6539
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2731, _2729, _2735
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft',)


class BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft(_2735.BevelGearSetSteadyStateSynchronousResponseOnAShaft):
    '''BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6539.BevelDifferentialGearSetLoadCase':
        '''BevelDifferentialGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6539.BevelDifferentialGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def bevel_differential_gears_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2731.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft]':
        '''List[BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft]: 'BevelDifferentialGearsSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsSteadyStateSynchronousResponseOnAShaft, constructor.new(_2731.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def bevel_differential_meshes_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2729.BevelDifferentialGearMeshSteadyStateSynchronousResponseOnAShaft]':
        '''List[BevelDifferentialGearMeshSteadyStateSynchronousResponseOnAShaft]: 'BevelDifferentialMeshesSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesSteadyStateSynchronousResponseOnAShaft, constructor.new(_2729.BevelDifferentialGearMeshSteadyStateSynchronousResponseOnAShaft))
        return value
