'''_6324.py

HypoidGearSetCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6624
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6322, _6323, _6264
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'HypoidGearSetCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCriticalSpeedAnalysis',)


class HypoidGearSetCriticalSpeedAnalysis(_6264.AGMAGleasonConicalGearSetCriticalSpeedAnalysis):
    '''HypoidGearSetCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6624.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6624.HypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def hypoid_gears_critical_speed_analysis(self) -> 'List[_6322.HypoidGearCriticalSpeedAnalysis]':
        '''List[HypoidGearCriticalSpeedAnalysis]: 'HypoidGearsCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCriticalSpeedAnalysis, constructor.new(_6322.HypoidGearCriticalSpeedAnalysis))
        return value

    @property
    def hypoid_meshes_critical_speed_analysis(self) -> 'List[_6323.HypoidGearMeshCriticalSpeedAnalysis]':
        '''List[HypoidGearMeshCriticalSpeedAnalysis]: 'HypoidMeshesCriticalSpeedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCriticalSpeedAnalysis, constructor.new(_6323.HypoidGearMeshCriticalSpeedAnalysis))
        return value
