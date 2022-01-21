'''_4543.py

StraightBevelGearSetCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.gears import _2288
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4541, _4542, _4451
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4414
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'StraightBevelGearSetCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearSetCompoundModalAnalysisAtAStiffness',)


class StraightBevelGearSetCompoundModalAnalysisAtAStiffness(_4451.BevelGearSetCompoundModalAnalysisAtAStiffness):
    '''StraightBevelGearSetCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearSetCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2288.StraightBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2288.StraightBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def straight_bevel_gears_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4541.StraightBevelGearCompoundModalAnalysisAtAStiffness]':
        '''List[StraightBevelGearCompoundModalAnalysisAtAStiffness]: 'StraightBevelGearsCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearsCompoundModalAnalysisAtAStiffness, constructor.new(_4541.StraightBevelGearCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def straight_bevel_meshes_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4542.StraightBevelGearMeshCompoundModalAnalysisAtAStiffness]':
        '''List[StraightBevelGearMeshCompoundModalAnalysisAtAStiffness]: 'StraightBevelMeshesCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelMeshesCompoundModalAnalysisAtAStiffness, constructor.new(_4542.StraightBevelGearMeshCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4414.StraightBevelGearSetModalAnalysisAtAStiffness]':
        '''List[StraightBevelGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4414.StraightBevelGearSetModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4414.StraightBevelGearSetModalAnalysisAtAStiffness]':
        '''List[StraightBevelGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4414.StraightBevelGearSetModalAnalysisAtAStiffness))
        return value
