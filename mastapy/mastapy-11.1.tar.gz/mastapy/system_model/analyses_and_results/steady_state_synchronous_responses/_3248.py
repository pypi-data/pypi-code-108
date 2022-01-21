'''_3248.py

BevelDifferentialGearSetSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6539
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3249, _3247, _3253
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'BevelDifferentialGearSetSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetSteadyStateSynchronousResponse',)


class BevelDifferentialGearSetSteadyStateSynchronousResponse(_3253.BevelGearSetSteadyStateSynchronousResponse):
    '''BevelDifferentialGearSetSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetSteadyStateSynchronousResponse.TYPE'):
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
    def bevel_differential_gears_steady_state_synchronous_response(self) -> 'List[_3249.BevelDifferentialGearSteadyStateSynchronousResponse]':
        '''List[BevelDifferentialGearSteadyStateSynchronousResponse]: 'BevelDifferentialGearsSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsSteadyStateSynchronousResponse, constructor.new(_3249.BevelDifferentialGearSteadyStateSynchronousResponse))
        return value

    @property
    def bevel_differential_meshes_steady_state_synchronous_response(self) -> 'List[_3247.BevelDifferentialGearMeshSteadyStateSynchronousResponse]':
        '''List[BevelDifferentialGearMeshSteadyStateSynchronousResponse]: 'BevelDifferentialMeshesSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesSteadyStateSynchronousResponse, constructor.new(_3247.BevelDifferentialGearMeshSteadyStateSynchronousResponse))
        return value
