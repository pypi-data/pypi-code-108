'''_2973.py

WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2971, _2972, _2908
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2843
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2908.GearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def worm_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2971.WormGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[WormGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'WormGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2971.WormGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def worm_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2972.WormGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[WormGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'WormMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2972.WormGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2843.WormGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[WormGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2843.WormGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2843.WormGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[WormGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2843.WormGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
