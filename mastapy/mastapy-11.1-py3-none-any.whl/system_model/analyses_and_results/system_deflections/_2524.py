'''_2524.py

PlanetaryConnectionSystemDeflection
'''


from mastapy.system_model.connections_and_sockets import _2029
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6650
from mastapy.system_model.analyses_and_results.power_flows import _3849
from mastapy.system_model.analyses_and_results.system_deflections import _2540
from mastapy._internal.python_net import python_net_import

_PLANETARY_CONNECTION_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'PlanetaryConnectionSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryConnectionSystemDeflection',)


class PlanetaryConnectionSystemDeflection(_2540.ShaftToMountableComponentConnectionSystemDeflection):
    '''PlanetaryConnectionSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_CONNECTION_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryConnectionSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2029.PlanetaryConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6650.PlanetaryConnectionLoadCase':
        '''PlanetaryConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6650.PlanetaryConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3849.PlanetaryConnectionPowerFlow':
        '''PlanetaryConnectionPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3849.PlanetaryConnectionPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
