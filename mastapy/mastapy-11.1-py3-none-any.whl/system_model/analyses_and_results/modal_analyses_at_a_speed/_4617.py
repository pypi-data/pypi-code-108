'''_4617.py

FaceGearSetModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4616, _4615, _4622
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'FaceGearSetModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetModalAnalysisAtASpeed',)


class FaceGearSetModalAnalysisAtASpeed(_4622.GearSetModalAnalysisAtASpeed):
    '''FaceGearSetModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2269.FaceGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6601.FaceGearSetLoadCase':
        '''FaceGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6601.FaceGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def face_gears_modal_analysis_at_a_speed(self) -> 'List[_4616.FaceGearModalAnalysisAtASpeed]':
        '''List[FaceGearModalAnalysisAtASpeed]: 'FaceGearsModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsModalAnalysisAtASpeed, constructor.new(_4616.FaceGearModalAnalysisAtASpeed))
        return value

    @property
    def face_meshes_modal_analysis_at_a_speed(self) -> 'List[_4615.FaceGearMeshModalAnalysisAtASpeed]':
        '''List[FaceGearMeshModalAnalysisAtASpeed]: 'FaceMeshesModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesModalAnalysisAtASpeed, constructor.new(_4615.FaceGearMeshModalAnalysisAtASpeed))
        return value
