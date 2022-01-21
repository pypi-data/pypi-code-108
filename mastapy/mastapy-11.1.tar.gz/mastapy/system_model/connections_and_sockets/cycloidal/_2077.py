'''_2077.py

CycloidalDiscCentralBearingConnection
'''


from mastapy.system_model.connections_and_sockets import _2011
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscCentralBearingConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCentralBearingConnection',)


class CycloidalDiscCentralBearingConnection(_2011.CoaxialConnection):
    '''CycloidalDiscCentralBearingConnection

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCentralBearingConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
