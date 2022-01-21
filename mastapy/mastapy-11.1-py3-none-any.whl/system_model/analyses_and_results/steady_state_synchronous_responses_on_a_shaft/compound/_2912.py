'''_2912.py

HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2910, _2911, _2854
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2781
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2854.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def hypoid_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2910.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'HypoidGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2910.HypoidGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def hypoid_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2911.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'HypoidMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2911.HypoidGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2781.HypoidGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2781.HypoidGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2781.HypoidGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[HypoidGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2781.HypoidGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
