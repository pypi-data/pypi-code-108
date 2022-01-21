'''_3599.py

SpiralBevelGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2284
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6674
from mastapy.system_model.analyses_and_results.stability_analyses import _3600, _3598, _3515
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'SpiralBevelGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetStabilityAnalysis',)


class SpiralBevelGearSetStabilityAnalysis(_3515.BevelGearSetStabilityAnalysis):
    '''SpiralBevelGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2284.SpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6674.SpiralBevelGearSetLoadCase':
        '''SpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6674.SpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def spiral_bevel_gears_stability_analysis(self) -> 'List[_3600.SpiralBevelGearStabilityAnalysis]':
        '''List[SpiralBevelGearStabilityAnalysis]: 'SpiralBevelGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearsStabilityAnalysis, constructor.new(_3600.SpiralBevelGearStabilityAnalysis))
        return value

    @property
    def spiral_bevel_meshes_stability_analysis(self) -> 'List[_3598.SpiralBevelGearMeshStabilityAnalysis]':
        '''List[SpiralBevelGearMeshStabilityAnalysis]: 'SpiralBevelMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshesStabilityAnalysis, constructor.new(_3598.SpiralBevelGearMeshStabilityAnalysis))
        return value
