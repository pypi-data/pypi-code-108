'''_3553.py

FaceGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.system_model.analyses_and_results.stability_analyses import _3554, _3552, _3558
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'FaceGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetStabilityAnalysis',)


class FaceGearSetStabilityAnalysis(_3558.GearSetStabilityAnalysis):
    '''FaceGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetStabilityAnalysis.TYPE'):
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
    def face_gears_stability_analysis(self) -> 'List[_3554.FaceGearStabilityAnalysis]':
        '''List[FaceGearStabilityAnalysis]: 'FaceGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsStabilityAnalysis, constructor.new(_3554.FaceGearStabilityAnalysis))
        return value

    @property
    def face_meshes_stability_analysis(self) -> 'List[_3552.FaceGearMeshStabilityAnalysis]':
        '''List[FaceGearMeshStabilityAnalysis]: 'FaceMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesStabilityAnalysis, constructor.new(_3552.FaceGearMeshStabilityAnalysis))
        return value
