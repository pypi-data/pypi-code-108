'''_3938.py

CVTBeltConnectionCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3805
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3907
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CVTBeltConnectionCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionCompoundPowerFlow',)


class CVTBeltConnectionCompoundPowerFlow(_3907.BeltConnectionCompoundPowerFlow):
    '''CVTBeltConnectionCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3805.CVTBeltConnectionPowerFlow]':
        '''List[CVTBeltConnectionPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3805.CVTBeltConnectionPowerFlow))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3805.CVTBeltConnectionPowerFlow]':
        '''List[CVTBeltConnectionPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3805.CVTBeltConnectionPowerFlow))
        return value
