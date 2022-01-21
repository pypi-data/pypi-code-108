'''_6691.py

TorqueConverterConnectionLoadCase
'''


from mastapy.system_model.connections_and_sockets.couplings import _2094
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6565
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_CONNECTION_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TorqueConverterConnectionLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterConnectionLoadCase',)


class TorqueConverterConnectionLoadCase(_6565.CouplingConnectionLoadCase):
    '''TorqueConverterConnectionLoadCase

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_CONNECTION_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterConnectionLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2094.TorqueConverterConnection':
        '''TorqueConverterConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2094.TorqueConverterConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
