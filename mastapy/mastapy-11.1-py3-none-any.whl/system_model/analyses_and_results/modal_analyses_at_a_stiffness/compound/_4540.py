'''_4540.py

StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4538, _4539, _4451
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4411
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness',)


class StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness(_4451.BevelGearSetCompoundModalAnalysisAtAStiffness):
    '''StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_diff_gears_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4538.StraightBevelDiffGearCompoundModalAnalysisAtAStiffness]':
        '''List[StraightBevelDiffGearCompoundModalAnalysisAtAStiffness]: 'StraightBevelDiffGearsCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsCompoundModalAnalysisAtAStiffness, constructor.new(_4538.StraightBevelDiffGearCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def straight_bevel_diff_meshes_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4539.StraightBevelDiffGearMeshCompoundModalAnalysisAtAStiffness]':
        '''List[StraightBevelDiffGearMeshCompoundModalAnalysisAtAStiffness]: 'StraightBevelDiffMeshesCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesCompoundModalAnalysisAtAStiffness, constructor.new(_4539.StraightBevelDiffGearMeshCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4411.StraightBevelDiffGearSetModalAnalysisAtAStiffness]':
        '''List[StraightBevelDiffGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4411.StraightBevelDiffGearSetModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4411.StraightBevelDiffGearSetModalAnalysisAtAStiffness]':
        '''List[StraightBevelDiffGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4411.StraightBevelDiffGearSetModalAnalysisAtAStiffness))
        return value
