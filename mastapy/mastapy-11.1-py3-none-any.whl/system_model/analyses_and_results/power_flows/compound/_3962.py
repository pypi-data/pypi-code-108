'''_3962.py

HypoidGearSetCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3960, _3961, _3904
from mastapy.system_model.analyses_and_results.power_flows import _3830
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'HypoidGearSetCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundPowerFlow',)


class HypoidGearSetCompoundPowerFlow(_3904.AGMAGleasonConicalGearSetCompoundPowerFlow):
    '''HypoidGearSetCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def hypoid_gears_compound_power_flow(self) -> 'List[_3960.HypoidGearCompoundPowerFlow]':
        '''List[HypoidGearCompoundPowerFlow]: 'HypoidGearsCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundPowerFlow, constructor.new(_3960.HypoidGearCompoundPowerFlow))
        return value

    @property
    def hypoid_meshes_compound_power_flow(self) -> 'List[_3961.HypoidGearMeshCompoundPowerFlow]':
        '''List[HypoidGearMeshCompoundPowerFlow]: 'HypoidMeshesCompoundPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundPowerFlow, constructor.new(_3961.HypoidGearMeshCompoundPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3830.HypoidGearSetPowerFlow]':
        '''List[HypoidGearSetPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3830.HypoidGearSetPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3830.HypoidGearSetPowerFlow]':
        '''List[HypoidGearSetPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3830.HypoidGearSetPowerFlow))
        return value
