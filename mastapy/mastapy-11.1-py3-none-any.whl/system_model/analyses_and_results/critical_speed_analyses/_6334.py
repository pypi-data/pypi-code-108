'''_6334.py

KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2281
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6637
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6332, _6333, _6328
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis',)


class KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis(_6328.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gears_critical_speed_analysis(self) -> 'List[_6332.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis]: 'KlingelnbergCycloPalloidSpiralBevelGearsCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearsCriticalSpeedAnalysis, constructor.new(_6332.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshes_critical_speed_analysis(self) -> 'List[_6333.KlingelnbergCycloPalloidSpiralBevelGearMeshCriticalSpeedAnalysis]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshCriticalSpeedAnalysis]: 'KlingelnbergCycloPalloidSpiralBevelMeshesCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshesCriticalSpeedAnalysis, constructor.new(_6333.KlingelnbergCycloPalloidSpiralBevelGearMeshCriticalSpeedAnalysis))
        return value
