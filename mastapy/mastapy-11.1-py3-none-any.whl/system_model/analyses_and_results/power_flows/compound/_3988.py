'''_3988.py

RingPinsToDiscConnectionCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.connections_and_sockets.cycloidal import _2083
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3858
from mastapy.system_model.analyses_and_results.power_flows.compound import _3963
from mastapy._internal.python_net import python_net_import

_RING_PINS_TO_DISC_CONNECTION_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'RingPinsToDiscConnectionCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsToDiscConnectionCompoundPowerFlow',)


class RingPinsToDiscConnectionCompoundPowerFlow(_3963.InterMountableComponentConnectionCompoundPowerFlow):
    '''RingPinsToDiscConnectionCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_TO_DISC_CONNECTION_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsToDiscConnectionCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2083.RingPinsToDiscConnection':
        '''RingPinsToDiscConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2083.RingPinsToDiscConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2083.RingPinsToDiscConnection':
        '''RingPinsToDiscConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2083.RingPinsToDiscConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3858.RingPinsToDiscConnectionPowerFlow]':
        '''List[RingPinsToDiscConnectionPowerFlow]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3858.RingPinsToDiscConnectionPowerFlow))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3858.RingPinsToDiscConnectionPowerFlow]':
        '''List[RingPinsToDiscConnectionPowerFlow]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3858.RingPinsToDiscConnectionPowerFlow))
        return value
