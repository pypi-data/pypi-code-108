'''_5731.py

FaceGearSetHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.system_model.analyses_and_results.system_deflections import _2490
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5729, _5730, _5740
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'FaceGearSetHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetHarmonicAnalysis',)


class FaceGearSetHarmonicAnalysis(_5740.GearSetHarmonicAnalysis):
    '''FaceGearSetHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetHarmonicAnalysis.TYPE'):
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
    def system_deflection_results(self) -> '_2490.FaceGearSetSystemDeflection':
        '''FaceGearSetSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2490.FaceGearSetSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def gears_harmonic_analysis(self) -> 'List[_5729.FaceGearHarmonicAnalysis]':
        '''List[FaceGearHarmonicAnalysis]: 'GearsHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearsHarmonicAnalysis, constructor.new(_5729.FaceGearHarmonicAnalysis))
        return value

    @property
    def face_gears_harmonic_analysis(self) -> 'List[_5729.FaceGearHarmonicAnalysis]':
        '''List[FaceGearHarmonicAnalysis]: 'FaceGearsHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsHarmonicAnalysis, constructor.new(_5729.FaceGearHarmonicAnalysis))
        return value

    @property
    def meshes_harmonic_analysis(self) -> 'List[_5730.FaceGearMeshHarmonicAnalysis]':
        '''List[FaceGearMeshHarmonicAnalysis]: 'MeshesHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshesHarmonicAnalysis, constructor.new(_5730.FaceGearMeshHarmonicAnalysis))
        return value

    @property
    def face_meshes_harmonic_analysis(self) -> 'List[_5730.FaceGearMeshHarmonicAnalysis]':
        '''List[FaceGearMeshHarmonicAnalysis]: 'FaceMeshesHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesHarmonicAnalysis, constructor.new(_5730.FaceGearMeshHarmonicAnalysis))
        return value
