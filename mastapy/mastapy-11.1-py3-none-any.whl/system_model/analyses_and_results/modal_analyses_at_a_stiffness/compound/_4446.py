'''_4446.py

BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4444, _4445, _4451
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4316
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness',)


class BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness(_4451.BevelGearSetCompoundModalAnalysisAtAStiffness):
    '''BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def bevel_differential_gears_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4444.BevelDifferentialGearCompoundModalAnalysisAtAStiffness]':
        '''List[BevelDifferentialGearCompoundModalAnalysisAtAStiffness]: 'BevelDifferentialGearsCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsCompoundModalAnalysisAtAStiffness, constructor.new(_4444.BevelDifferentialGearCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def bevel_differential_meshes_compound_modal_analysis_at_a_stiffness(self) -> 'List[_4445.BevelDifferentialGearMeshCompoundModalAnalysisAtAStiffness]':
        '''List[BevelDifferentialGearMeshCompoundModalAnalysisAtAStiffness]: 'BevelDifferentialMeshesCompoundModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesCompoundModalAnalysisAtAStiffness, constructor.new(_4445.BevelDifferentialGearMeshCompoundModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4316.BevelDifferentialGearSetModalAnalysisAtAStiffness]':
        '''List[BevelDifferentialGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4316.BevelDifferentialGearSetModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4316.BevelDifferentialGearSetModalAnalysisAtAStiffness]':
        '''List[BevelDifferentialGearSetModalAnalysisAtAStiffness]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4316.BevelDifferentialGearSetModalAnalysisAtAStiffness))
        return value
