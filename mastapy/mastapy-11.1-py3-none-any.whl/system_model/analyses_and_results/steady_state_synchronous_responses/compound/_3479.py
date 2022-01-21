'''_3479.py

StraightBevelGearSetCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model.gears import _2288
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3477, _3478, _3387
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3349
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'StraightBevelGearSetCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearSetCompoundSteadyStateSynchronousResponse',)


class StraightBevelGearSetCompoundSteadyStateSynchronousResponse(_3387.BevelGearSetCompoundSteadyStateSynchronousResponse):
    '''StraightBevelGearSetCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearSetCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2288.StraightBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2288.StraightBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_gears_compound_steady_state_synchronous_response(self) -> 'List[_3477.StraightBevelGearCompoundSteadyStateSynchronousResponse]':
        '''List[StraightBevelGearCompoundSteadyStateSynchronousResponse]: 'StraightBevelGearsCompoundSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearsCompoundSteadyStateSynchronousResponse, constructor.new(_3477.StraightBevelGearCompoundSteadyStateSynchronousResponse))
        return value

    @property
    def straight_bevel_meshes_compound_steady_state_synchronous_response(self) -> 'List[_3478.StraightBevelGearMeshCompoundSteadyStateSynchronousResponse]':
        '''List[StraightBevelGearMeshCompoundSteadyStateSynchronousResponse]: 'StraightBevelMeshesCompoundSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelMeshesCompoundSteadyStateSynchronousResponse, constructor.new(_3478.StraightBevelGearMeshCompoundSteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3349.StraightBevelGearSetSteadyStateSynchronousResponse]':
        '''List[StraightBevelGearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3349.StraightBevelGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3349.StraightBevelGearSetSteadyStateSynchronousResponse]':
        '''List[StraightBevelGearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3349.StraightBevelGearSetSteadyStateSynchronousResponse))
        return value
