'''_3998.py

SpiralBevelGearMeshCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.connections_and_sockets.gears import _2065
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3867
from mastapy.system_model.analyses_and_results.power_flows.compound import _3915
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_MESH_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SpiralBevelGearMeshCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearMeshCompoundPowerFlow',)


class SpiralBevelGearMeshCompoundPowerFlow(_3915.BevelGearMeshCompoundPowerFlow):
    '''SpiralBevelGearMeshCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_MESH_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearMeshCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2065.SpiralBevelGearMesh':
        '''SpiralBevelGearMesh: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2065.SpiralBevelGearMesh)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2065.SpiralBevelGearMesh':
        '''SpiralBevelGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2065.SpiralBevelGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3867.SpiralBevelGearMeshPowerFlow]':
        '''List[SpiralBevelGearMeshPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3867.SpiralBevelGearMeshPowerFlow))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3867.SpiralBevelGearMeshPowerFlow]':
        '''List[SpiralBevelGearMeshPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3867.SpiralBevelGearMeshPowerFlow))
        return value
