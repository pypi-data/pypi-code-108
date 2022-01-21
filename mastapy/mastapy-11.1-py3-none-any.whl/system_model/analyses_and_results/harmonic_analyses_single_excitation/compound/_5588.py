'''_5588.py

FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5586, _5587, _5593
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5458
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation',)


class FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation(_5593.GearSetCompoundHarmonicAnalysisOfSingleExcitation):
    '''FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
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
    def face_gears_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5586.FaceGearCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearCompoundHarmonicAnalysisOfSingleExcitation]: 'FaceGearsCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5586.FaceGearCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def face_meshes_compound_harmonic_analysis_of_single_excitation(self) -> 'List[_5587.FaceGearMeshCompoundHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearMeshCompoundHarmonicAnalysisOfSingleExcitation]: 'FaceMeshesCompoundHarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesCompoundHarmonicAnalysisOfSingleExcitation, constructor.new(_5587.FaceGearMeshCompoundHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation]':
        '''List[FaceGearSetHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5458.FaceGearSetHarmonicAnalysisOfSingleExcitation))
        return value
