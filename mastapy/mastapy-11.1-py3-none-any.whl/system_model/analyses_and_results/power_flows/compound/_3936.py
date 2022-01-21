'''_3936.py

CouplingConnectionCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3802
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3963
from mastapy._internal.python_net import python_net_import

_COUPLING_CONNECTION_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CouplingConnectionCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingConnectionCompoundPowerFlow',)


class CouplingConnectionCompoundPowerFlow(_3963.InterMountableComponentConnectionCompoundPowerFlow):
    '''CouplingConnectionCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _COUPLING_CONNECTION_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingConnectionCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3802.CouplingConnectionPowerFlow]':
        '''List[CouplingConnectionPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3802.CouplingConnectionPowerFlow))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3802.CouplingConnectionPowerFlow]':
        '''List[CouplingConnectionPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3802.CouplingConnectionPowerFlow))
        return value
