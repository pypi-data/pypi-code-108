'''_3897.py

ZerolBevelGearSetPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6706
from mastapy.gears.rating.zerol_bevel import _337
from mastapy.system_model.analyses_and_results.power_flows import _3896, _3895, _3783
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'ZerolBevelGearSetPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetPowerFlow',)


class ZerolBevelGearSetPowerFlow(_3783.BevelGearSetPowerFlow):
    '''ZerolBevelGearSetPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6706.ZerolBevelGearSetLoadCase':
        '''ZerolBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6706.ZerolBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def rating(self) -> '_337.ZerolBevelGearSetRating':
        '''ZerolBevelGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_337.ZerolBevelGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_337.ZerolBevelGearSetRating':
        '''ZerolBevelGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_337.ZerolBevelGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def gears_power_flow(self) -> 'List[_3896.ZerolBevelGearPowerFlow]':
        '''List[ZerolBevelGearPowerFlow]: 'GearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearsPowerFlow, constructor.new(_3896.ZerolBevelGearPowerFlow))
        return value

    @property
    def zerol_bevel_gears_power_flow(self) -> 'List[_3896.ZerolBevelGearPowerFlow]':
        '''List[ZerolBevelGearPowerFlow]: 'ZerolBevelGearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearsPowerFlow, constructor.new(_3896.ZerolBevelGearPowerFlow))
        return value

    @property
    def meshes_power_flow(self) -> 'List[_3895.ZerolBevelGearMeshPowerFlow]':
        '''List[ZerolBevelGearMeshPowerFlow]: 'MeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshesPowerFlow, constructor.new(_3895.ZerolBevelGearMeshPowerFlow))
        return value

    @property
    def zerol_bevel_meshes_power_flow(self) -> 'List[_3895.ZerolBevelGearMeshPowerFlow]':
        '''List[ZerolBevelGearMeshPowerFlow]: 'ZerolBevelMeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshesPowerFlow, constructor.new(_3895.ZerolBevelGearMeshPowerFlow))
        return value
