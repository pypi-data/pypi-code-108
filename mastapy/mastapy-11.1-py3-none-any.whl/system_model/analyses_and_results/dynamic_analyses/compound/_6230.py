'''_6230.py

StraightBevelDiffGearSetCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6228, _6229, _6141
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6101
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'StraightBevelDiffGearSetCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetCompoundDynamicAnalysis',)


class StraightBevelDiffGearSetCompoundDynamicAnalysis(_6141.BevelGearSetCompoundDynamicAnalysis):
    '''StraightBevelDiffGearSetCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetCompoundDynamicAnalysis.TYPE'):
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
    def straight_bevel_diff_gears_compound_dynamic_analysis(self) -> 'List[_6228.StraightBevelDiffGearCompoundDynamicAnalysis]':
        '''List[StraightBevelDiffGearCompoundDynamicAnalysis]: 'StraightBevelDiffGearsCompoundDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsCompoundDynamicAnalysis, constructor.new(_6228.StraightBevelDiffGearCompoundDynamicAnalysis))
        return value

    @property
    def straight_bevel_diff_meshes_compound_dynamic_analysis(self) -> 'List[_6229.StraightBevelDiffGearMeshCompoundDynamicAnalysis]':
        '''List[StraightBevelDiffGearMeshCompoundDynamicAnalysis]: 'StraightBevelDiffMeshesCompoundDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesCompoundDynamicAnalysis, constructor.new(_6229.StraightBevelDiffGearMeshCompoundDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6101.StraightBevelDiffGearSetDynamicAnalysis]':
        '''List[StraightBevelDiffGearSetDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6101.StraightBevelDiffGearSetDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6101.StraightBevelDiffGearSetDynamicAnalysis]':
        '''List[StraightBevelDiffGearSetDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6101.StraightBevelDiffGearSetDynamicAnalysis))
        return value
