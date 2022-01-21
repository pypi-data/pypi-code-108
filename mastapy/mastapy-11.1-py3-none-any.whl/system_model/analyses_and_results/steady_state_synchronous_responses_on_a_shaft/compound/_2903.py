'''_2903.py

FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import _2901, _2902, _2908
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2772
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound', 'FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft',)


class FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft(_2908.GearSetCompoundSteadyStateSynchronousResponseOnAShaft):
    '''FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetCompoundSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2269.FaceGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2269.FaceGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def face_gears_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2901.FaceGearCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[FaceGearCompoundSteadyStateSynchronousResponseOnAShaft]: 'FaceGearsCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2901.FaceGearCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def face_meshes_compound_steady_state_synchronous_response_on_a_shaft(self) -> 'List[_2902.FaceGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]':
        '''List[FaceGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]: 'FaceMeshesCompoundSteadyStateSynchronousResponseOnAShaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesCompoundSteadyStateSynchronousResponseOnAShaft, constructor.new(_2902.FaceGearMeshCompoundSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2772.FaceGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[FaceGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2772.FaceGearSetSteadyStateSynchronousResponseOnAShaft))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2772.FaceGearSetSteadyStateSynchronousResponseOnAShaft]':
        '''List[FaceGearSetSteadyStateSynchronousResponseOnAShaft]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2772.FaceGearSetSteadyStateSynchronousResponseOnAShaft))
        return value
