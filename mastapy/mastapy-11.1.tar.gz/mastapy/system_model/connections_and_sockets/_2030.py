'''_2030.py

PlanetarySocket
'''


from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets import _2031
from mastapy._internal.python_net import python_net_import

_PLANETARY_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'PlanetarySocket')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetarySocket',)


class PlanetarySocket(_2031.PlanetarySocketBase):
    '''PlanetarySocket

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetarySocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planet_tip_clearance(self) -> 'float':
        '''float: 'PlanetTipClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PlanetTipClearance
