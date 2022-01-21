'''_2024.py

MountableComponentInnerSocket
'''


from mastapy.system_model.connections_and_sockets import _2026
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_INNER_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'MountableComponentInnerSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentInnerSocket',)


class MountableComponentInnerSocket(_2026.MountableComponentSocket):
    '''MountableComponentInnerSocket

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_INNER_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentInnerSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
