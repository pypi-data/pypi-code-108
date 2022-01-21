'''_2075.py

CycloidalDiscAxialLeftSocket
'''


from mastapy.system_model.connections_and_sockets import _2022
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_AXIAL_LEFT_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscAxialLeftSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscAxialLeftSocket',)


class CycloidalDiscAxialLeftSocket(_2022.InnerShaftSocketBase):
    '''CycloidalDiscAxialLeftSocket

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_AXIAL_LEFT_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscAxialLeftSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
