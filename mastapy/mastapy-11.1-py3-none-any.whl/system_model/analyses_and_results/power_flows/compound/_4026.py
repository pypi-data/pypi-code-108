'''_4026.py

ZerolBevelGearSetCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _4024, _4025, _3916
from mastapy.system_model.analyses_and_results.power_flows import _3897
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'ZerolBevelGearSetCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetCompoundPowerFlow',)


class ZerolBevelGearSetCompoundPowerFlow(_3916.BevelGearSetCompoundPowerFlow):
    '''ZerolBevelGearSetCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def zerol_bevel_gears_compound_power_flow(self) -> 'List[_4024.ZerolBevelGearCompoundPowerFlow]':
        '''List[ZerolBevelGearCompoundPowerFlow]: 'ZerolBevelGearsCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearsCompoundPowerFlow, constructor.new(_4024.ZerolBevelGearCompoundPowerFlow))
        return value

    @property
    def zerol_bevel_meshes_compound_power_flow(self) -> 'List[_4025.ZerolBevelGearMeshCompoundPowerFlow]':
        '''List[ZerolBevelGearMeshCompoundPowerFlow]: 'ZerolBevelMeshesCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshesCompoundPowerFlow, constructor.new(_4025.ZerolBevelGearMeshCompoundPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3897.ZerolBevelGearSetPowerFlow]':
        '''List[ZerolBevelGearSetPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3897.ZerolBevelGearSetPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3897.ZerolBevelGearSetPowerFlow]':
        '''List[ZerolBevelGearSetPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3897.ZerolBevelGearSetPowerFlow))
        return value
