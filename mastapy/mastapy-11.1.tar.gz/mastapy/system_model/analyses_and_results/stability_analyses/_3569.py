'''_3569.py

KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2279
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6634
from mastapy.system_model.analyses_and_results.stability_analyses import _3570, _3568, _3566
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis',)


class KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis(_3566.KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis):
    '''KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase':
        '''KlingelnbergCycloPalloidHypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears_stability_analysis(self) -> 'List[_3570.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearStabilityAnalysis]: 'KlingelnbergCycloPalloidHypoidGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsStabilityAnalysis, constructor.new(_3570.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_stability_analysis(self) -> 'List[_3568.KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis]: 'KlingelnbergCycloPalloidHypoidMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesStabilityAnalysis, constructor.new(_3568.KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis))
        return value
