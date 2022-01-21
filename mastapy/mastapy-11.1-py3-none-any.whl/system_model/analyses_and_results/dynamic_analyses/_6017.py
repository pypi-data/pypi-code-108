'''_6017.py

CoaxialConnectionDynamicAnalysis
'''


from mastapy.system_model.connections_and_sockets import _2011
from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets.cycloidal import _2077
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6550, _6572
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6091
from mastapy._internal.python_net import python_net_import

_COAXIAL_CONNECTION_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'CoaxialConnectionDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CoaxialConnectionDynamicAnalysis',)


class CoaxialConnectionDynamicAnalysis(_6091.ShaftToMountableComponentConnectionDynamicAnalysis):
    '''CoaxialConnectionDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COAXIAL_CONNECTION_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CoaxialConnectionDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2011.CoaxialConnection':
        '''CoaxialConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2011.CoaxialConnection.TYPE not in self.wrapped.ConnectionDesign.__class__.__mro__:
            raise CastException('Failed to cast connection_design to CoaxialConnection. Expected: {}.'.format(self.wrapped.ConnectionDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionDesign.__class__)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6550.CoaxialConnectionLoadCase':
        '''CoaxialConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6550.CoaxialConnectionLoadCase.TYPE not in self.wrapped.ConnectionLoadCase.__class__.__mro__:
            raise CastException('Failed to cast connection_load_case to CoaxialConnectionLoadCase. Expected: {}.'.format(self.wrapped.ConnectionLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionLoadCase.__class__)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None
