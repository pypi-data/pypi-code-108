'''_3933.py

ConnectionCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3800
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7256
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'ConnectionCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundPowerFlow',)


class ConnectionCompoundPowerFlow(_7256.ConnectionCompoundAnalysis):
    '''ConnectionCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3800.ConnectionPowerFlow]':
        '''List[ConnectionPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3800.ConnectionPowerFlow))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3800.ConnectionPowerFlow]':
        '''List[ConnectionPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3800.ConnectionPowerFlow))
        return value
