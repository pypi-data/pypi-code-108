'''_2879.py

ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2262
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2877, _2878, _2908
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2748
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2908.GearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def concept_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2877.ConceptGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConceptGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'ConceptGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2877.ConceptGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def concept_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2878.ConceptGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConceptGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'ConceptMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2878.ConceptGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2748.ConceptGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConceptGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2748.ConceptGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2748.ConceptGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[ConceptGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2748.ConceptGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
