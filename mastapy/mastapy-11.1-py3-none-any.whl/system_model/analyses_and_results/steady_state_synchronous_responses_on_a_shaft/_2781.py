'''_2781.py

HypoidGearSetSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6624
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2782, _2780, _2723
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'HypoidGearSetSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetSteadyStateSynchronousResponseOnAShaft',)


class HypoidGearSetSteadyStateSynchronousResponseOnAShaft(_2723.AGMAGleasonConicalGearSetSteadyStateSynchronousResponseOnAShaft):
    '''HypoidGearSetSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6624.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6624.HypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def hypoid_gears_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2782.HypoidGearSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearSteadyStateSynchronousResponseOnAShaft]: 'HypoidGearsSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsSteadyStateSynchronousResponseOnAShaft, constructor.new(_2782.HypoidGearSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def hypoid_meshes_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2780.HypoidGearMeshSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearMeshSteadyStateSynchronousResponseOnAShaft]: 'HypoidMeshesSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesSteadyStateSynchronousResponseOnAShaft, constructor.new(_2780.HypoidGearMeshSteadyStateSynchronousResponseOnAShaft))
        return value
