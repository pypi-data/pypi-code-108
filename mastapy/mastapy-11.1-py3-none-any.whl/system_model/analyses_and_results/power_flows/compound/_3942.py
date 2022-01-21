'''_3942.py

CycloidalDiscCentralBearingConnectionCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3809
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3922
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CycloidalDiscCentralBearingConnectionCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCentralBearingConnectionCompoundPowerFlow',)


class CycloidalDiscCentralBearingConnectionCompoundPowerFlow(_3922.CoaxialConnectionCompoundPowerFlow):
    '''CycloidalDiscCentralBearingConnectionCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCentralBearingConnectionCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3809.CycloidalDiscCentralBearingConnectionPowerFlow]':
        '''List[CycloidalDiscCentralBearingConnectionPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3809.CycloidalDiscCentralBearingConnectionPowerFlow))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3809.CycloidalDiscCentralBearingConnectionPowerFlow]':
        '''List[CycloidalDiscCentralBearingConnectionPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3809.CycloidalDiscCentralBearingConnectionPowerFlow))
        return value
