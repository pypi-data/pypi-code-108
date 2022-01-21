'''_3805.py

CVTBeltConnectionPowerFlow
'''


from mastapy.system_model.connections_and_sockets import _2015
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3774
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'CVTBeltConnectionPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionPowerFlow',)


class CVTBeltConnectionPowerFlow(_3774.BeltConnectionPowerFlow):
    '''CVTBeltConnectionPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2015.CVTBeltConnection':
        '''CVTBeltConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2015.CVTBeltConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
