'''_3931.py

ConicalGearMeshCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3797
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3957
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'ConicalGearMeshCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundPowerFlow',)


class ConicalGearMeshCompoundPowerFlow(_3957.GearMeshCompoundPowerFlow):
    '''ConicalGearMeshCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3797.ConicalGearMeshPowerFlow]':
        '''List[ConicalGearMeshPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3797.ConicalGearMeshPowerFlow))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3797.ConicalGearMeshPowerFlow]':
        '''List[ConicalGearMeshPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3797.ConicalGearMeshPowerFlow))
        return value
