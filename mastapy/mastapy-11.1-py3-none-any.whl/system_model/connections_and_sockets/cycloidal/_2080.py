'''_2080.py

CycloidalDiscPlanetaryBearingConnection
'''


from mastapy.system_model.connections_and_sockets import _2007
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscPlanetaryBearingConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscPlanetaryBearingConnection',)


class CycloidalDiscPlanetaryBearingConnection(_2007.AbstractShaftToMountableComponentConnection):
    '''CycloidalDiscPlanetaryBearingConnection

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscPlanetaryBearingConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
