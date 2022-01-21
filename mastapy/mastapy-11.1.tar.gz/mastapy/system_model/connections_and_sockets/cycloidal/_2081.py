'''_2081.py

CycloidalDiscPlanetaryBearingSocket
'''


from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets import _2031
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_PLANETARY_BEARING_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscPlanetaryBearingSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscPlanetaryBearingSocket',)


class CycloidalDiscPlanetaryBearingSocket(_2031.PlanetarySocketBase):
    '''CycloidalDiscPlanetaryBearingSocket

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_PLANETARY_BEARING_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscPlanetaryBearingSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_for_eccentric_bearing(self) -> 'bool':
        '''bool: 'IsForEccentricBearing' is the original name of this property.'''

        return self.wrapped.IsForEccentricBearing

    @is_for_eccentric_bearing.setter
    def is_for_eccentric_bearing(self, value: 'bool'):
        self.wrapped.IsForEccentricBearing = bool(value) if value else False
