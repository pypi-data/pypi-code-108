'''_6101.py

StraightBevelDiffGearSetDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2286
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6680
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6099, _6100, _6011
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'StraightBevelDiffGearSetDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetDynamicAnalysis',)


class StraightBevelDiffGearSetDynamicAnalysis(_6011.BevelGearSetDynamicAnalysis):
    '''StraightBevelDiffGearSetDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2286.StraightBevelDiffGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6680.StraightBevelDiffGearSetLoadCase':
        '''StraightBevelDiffGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6680.StraightBevelDiffGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def straight_bevel_diff_gears_dynamic_analysis(self) -> 'List[_6099.StraightBevelDiffGearDynamicAnalysis]':
        '''List[StraightBevelDiffGearDynamicAnalysis]: 'StraightBevelDiffGearsDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearsDynamicAnalysis, constructor.new(_6099.StraightBevelDiffGearDynamicAnalysis))
        return value

    @property
    def straight_bevel_diff_meshes_dynamic_analysis(self) -> 'List[_6100.StraightBevelDiffGearMeshDynamicAnalysis]':
        '''List[StraightBevelDiffGearMeshDynamicAnalysis]: 'StraightBevelDiffMeshesDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshesDynamicAnalysis, constructor.new(_6100.StraightBevelDiffGearMeshDynamicAnalysis))
        return value
