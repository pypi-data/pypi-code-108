'''_3337.py

SpiralBevelGearSetSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model.gears import _2284
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6674
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3338, _3336, _3253
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'SpiralBevelGearSetSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetSteadyStateSynchronousResponse',)


class SpiralBevelGearSetSteadyStateSynchronousResponse(_3253.BevelGearSetSteadyStateSynchronousResponse):
    '''SpiralBevelGearSetSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2284.SpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6674.SpiralBevelGearSetLoadCase':
        '''SpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6674.SpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def spiral_bevel_gears_steady_state_synchronous_response(self) -> 'List[_3338.SpiralBevelGearSteadyStateSynchronousResponse]':
        '''List[SpiralBevelGearSteadyStateSynchronousResponse]: 'SpiralBevelGearsSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearsSteadyStateSynchronousResponse, constructor.new(_3338.SpiralBevelGearSteadyStateSynchronousResponse))
        return value

    @property
    def spiral_bevel_meshes_steady_state_synchronous_response(self) -> 'List[_3336.SpiralBevelGearMeshSteadyStateSynchronousResponse]':
        '''List[SpiralBevelGearMeshSteadyStateSynchronousResponse]: 'SpiralBevelMeshesSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshesSteadyStateSynchronousResponse, constructor.new(_3336.SpiralBevelGearMeshSteadyStateSynchronousResponse))
        return value
