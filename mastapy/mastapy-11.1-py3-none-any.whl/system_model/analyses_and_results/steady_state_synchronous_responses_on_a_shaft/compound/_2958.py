'''_2958.py

StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2288
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2956, _2957, _2866
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2828
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2866.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
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
    def straight_bevel_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2956.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'StraightBevelGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2956.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def straight_bevel_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2957.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'StraightBevelMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2957.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2828.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2828.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2828.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2828.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
