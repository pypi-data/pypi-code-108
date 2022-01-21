'''_5910.py

FaceGearSetCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5908, _5909, _5915
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5731
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'FaceGearSetCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetCompoundHarmonicAnalysis',)


class FaceGearSetCompoundHarmonicAnalysis(_5915.GearSetCompoundHarmonicAnalysis):
    '''FaceGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetCompoundHarmonicAnalysis.TYPE'):
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
    def face_gears_compound_harmonic_analysis(self) -> 'List[_5908.FaceGearCompoundHarmonicAnalysis]':
        '''List[FaceGearCompoundHarmonicAnalysis]: 'FaceGearsCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsCompoundHarmonicAnalysis, constructor.new(_5908.FaceGearCompoundHarmonicAnalysis))
        return value

    @property
    def face_meshes_compound_harmonic_analysis(self) -> 'List[_5909.FaceGearMeshCompoundHarmonicAnalysis]':
        '''List[FaceGearMeshCompoundHarmonicAnalysis]: 'FaceMeshesCompoundHarmonicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesCompoundHarmonicAnalysis, constructor.new(_5909.FaceGearMeshCompoundHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5731.FaceGearSetHarmonicAnalysis]':
        '''List[FaceGearSetHarmonicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5731.FaceGearSetHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5731.FaceGearSetHarmonicAnalysis]':
        '''List[FaceGearSetHarmonicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5731.FaceGearSetHarmonicAnalysis))
        return value
