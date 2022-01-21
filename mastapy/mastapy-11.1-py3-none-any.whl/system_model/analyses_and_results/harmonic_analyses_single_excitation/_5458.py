'''_5458.py

FaceGearSetHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5456, _5457, _5463
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'FaceGearSetHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetHarmonicAnalysisOfSingleExcitation',)


class FaceGearSetHarmonicAnalysisOfSingleExcitation(_5463.GearSetHarmonicAnalysisOfSingleExcitation):
    '''FaceGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetHarmonicAnalysisOfSingleExcitation.TYPE'):
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
    def face_gears_harmonic_analysis_of_single_excitation(self) -> 'List[_5456.FaceGearHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearHarmonicAnalysisOfSingleExcitation]: 'FaceGearsHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsHarmonicAnalysisOfSingleExcitation, constructor.new(_5456.FaceGearHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def face_meshes_harmonic_analysis_of_single_excitation(self) -> 'List[_5457.FaceGearMeshHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearMeshHarmonicAnalysisOfSingleExcitation]: 'FaceMeshesHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesHarmonicAnalysisOfSingleExcitation, constructor.new(_5457.FaceGearMeshHarmonicAnalysisOfSingleExcitation))
        return value
