'''_2035.py

RollingRingSocket
'''


from mastapy.system_model.connections_and_sockets import _2018
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'RollingRingSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingSocket',)


class RollingRingSocket(_2018.CylindricalSocket):
    '''RollingRingSocket

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
