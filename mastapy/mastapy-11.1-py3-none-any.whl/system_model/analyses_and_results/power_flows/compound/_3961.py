'''_3961.py

HypoidGearMeshCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.connections_and_sockets.gears import _2057
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3828
from mastapy.system_model.analyses_and_results.power_flows.compound import _3903
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_MESH_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'HypoidGearMeshCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearMeshCompoundPowerFlow',)


class HypoidGearMeshCompoundPowerFlow(_3903.AGMAGleasonConicalGearMeshCompoundPowerFlow):
    '''HypoidGearMeshCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_MESH_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearMeshCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2057.HypoidGearMesh)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2057.HypoidGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3828.HypoidGearMeshPowerFlow]':
        '''List[HypoidGearMeshPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3828.HypoidGearMeshPowerFlow))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3828.HypoidGearMeshPowerFlow]':
        '''List[HypoidGearMeshPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3828.HypoidGearMeshPowerFlow))
        return value
