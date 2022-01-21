'''_6444.py

FaceGearSetCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6442, _6443, _6449
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6315
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'FaceGearSetCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetCompoundCriticalSpeedAnalysis',)


class FaceGearSetCompoundCriticalSpeedAnalysis(_6449.GearSetCompoundCriticalSpeedAnalysis):
    '''FaceGearSetCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetCompoundCriticalSpeedAnalysis.TYPE'):
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
    def face_gears_compound_critical_speed_analysis(self) -> 'List[_6442.FaceGearCompoundCriticalSpeedAnalysis]':
        '''List[FaceGearCompoundCriticalSpeedAnalysis]: 'FaceGearsCompoundCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsCompoundCriticalSpeedAnalysis, constructor.new(_6442.FaceGearCompoundCriticalSpeedAnalysis))
        return value

    @property
    def face_meshes_compound_critical_speed_analysis(self) -> 'List[_6443.FaceGearMeshCompoundCriticalSpeedAnalysis]':
        '''List[FaceGearMeshCompoundCriticalSpeedAnalysis]: 'FaceMeshesCompoundCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesCompoundCriticalSpeedAnalysis, constructor.new(_6443.FaceGearMeshCompoundCriticalSpeedAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6315.FaceGearSetCriticalSpeedAnalysis]':
        '''List[FaceGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6315.FaceGearSetCriticalSpeedAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6315.FaceGearSetCriticalSpeedAnalysis]':
        '''List[FaceGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6315.FaceGearSetCriticalSpeedAnalysis))
        return value
