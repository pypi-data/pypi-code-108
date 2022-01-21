'''_3830.py

HypoidGearSetPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6624
from mastapy.gears.rating.hypoid import _406
from mastapy.system_model.analyses_and_results.power_flows import _3829, _3828, _3771
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'HypoidGearSetPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetPowerFlow',)


class HypoidGearSetPowerFlow(_3771.AGMAGleasonConicalGearSetPowerFlow):
    '''HypoidGearSetPowerFlow

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetPowerFlow.TYPE'):
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
    def rating(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def gears_power_flow(self) -> 'List[_3829.HypoidGearPowerFlow]':
        '''List[HypoidGearPowerFlow]: 'GearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearsPowerFlow, constructor.new(_3829.HypoidGearPowerFlow))
        return value

    @property
    def hypoid_gears_power_flow(self) -> 'List[_3829.HypoidGearPowerFlow]':
        '''List[HypoidGearPowerFlow]: 'HypoidGearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsPowerFlow, constructor.new(_3829.HypoidGearPowerFlow))
        return value

    @property
    def meshes_power_flow(self) -> 'List[_3828.HypoidGearMeshPowerFlow]':
        '''List[HypoidGearMeshPowerFlow]: 'MeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshesPowerFlow, constructor.new(_3828.HypoidGearMeshPowerFlow))
        return value

    @property
    def hypoid_meshes_power_flow(self) -> 'List[_3828.HypoidGearMeshPowerFlow]':
        '''List[HypoidGearMeshPowerFlow]: 'HypoidMeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesPowerFlow, constructor.new(_3828.HypoidGearMeshPowerFlow))
        return value
