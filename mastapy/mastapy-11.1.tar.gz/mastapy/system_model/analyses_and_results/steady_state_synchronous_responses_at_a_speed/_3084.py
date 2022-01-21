'''_3084.py

StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6680
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _3085, _3083, _2994
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed', 'StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed',)


class StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed(_2994.BevelGearSetSteadyStateSynchronousResponseAtASpeed):
    '''StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6680.StraightBevelDiffGearSetLoadCase':
        '''StraightBevelDiffGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6680.StraightBevelDiffGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def straight_bevel_diff_gears_steady_state_synchronous_response_at_a_speed(self) -> 'List[_3085.StraightBevelDiffGearSteadyStateSynchronousResponseAtASpeed]':
        '''List[StraightBevelDiffGearSteadyStateSynchronousResponseAtASpeed]: 'StraightBevelDiffGearsSteadyStateSynchronousResponseAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsSteadyStateSynchronousResponseAtASpeed, constructor.new(_3085.StraightBevelDiffGearSteadyStateSynchronousResponseAtASpeed))
        return value

    @property
    def straight_bevel_diff_meshes_steady_state_synchronous_response_at_a_speed(self) -> 'List[_3083.StraightBevelDiffGearMeshSteadyStateSynchronousResponseAtASpeed]':
        '''List[StraightBevelDiffGearMeshSteadyStateSynchronousResponseAtASpeed]: 'StraightBevelDiffMeshesSteadyStateSynchronousResponseAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesSteadyStateSynchronousResponseAtASpeed, constructor.new(_3083.StraightBevelDiffGearMeshSteadyStateSynchronousResponseAtASpeed))
        return value
