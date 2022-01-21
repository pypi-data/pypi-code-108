'''_3625.py

WormGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.stability_analyses import _3626, _3624, _3558
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'WormGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetStabilityAnalysis',)


class WormGearSetStabilityAnalysis(_3558.GearSetStabilityAnalysis):
    '''WormGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6703.WormGearSetLoadCase':
        '''WormGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6703.WormGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def worm_gears_stability_analysis(self) -> 'List[_3626.WormGearStabilityAnalysis]':
        '''List[WormGearStabilityAnalysis]: 'WormGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsStabilityAnalysis, constructor.new(_3626.WormGearStabilityAnalysis))
        return value

    @property
    def worm_meshes_stability_analysis(self) -> 'List[_3624.WormGearMeshStabilityAnalysis]':
        '''List[WormGearMeshStabilityAnalysis]: 'WormMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesStabilityAnalysis, constructor.new(_3624.WormGearMeshStabilityAnalysis))
        return value
