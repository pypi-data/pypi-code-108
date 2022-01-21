'''_3510.py

BevelDifferentialGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6539
from mastapy.system_model.analyses_and_results.stability_analyses import _3511, _3509, _3515
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'BevelDifferentialGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetStabilityAnalysis',)


class BevelDifferentialGearSetStabilityAnalysis(_3515.BevelGearSetStabilityAnalysis):
    '''BevelDifferentialGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6539.BevelDifferentialGearSetLoadCase':
        '''BevelDifferentialGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6539.BevelDifferentialGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def bevel_differential_gears_stability_analysis(self) -> 'List[_3511.BevelDifferentialGearStabilityAnalysis]':
        '''List[BevelDifferentialGearStabilityAnalysis]: 'BevelDifferentialGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsStabilityAnalysis, constructor.new(_3511.BevelDifferentialGearStabilityAnalysis))
        return value

    @property
    def bevel_differential_meshes_stability_analysis(self) -> 'List[_3509.BevelDifferentialGearMeshStabilityAnalysis]':
        '''List[BevelDifferentialGearMeshStabilityAnalysis]: 'BevelDifferentialMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesStabilityAnalysis, constructor.new(_3509.BevelDifferentialGearMeshStabilityAnalysis))
        return value
