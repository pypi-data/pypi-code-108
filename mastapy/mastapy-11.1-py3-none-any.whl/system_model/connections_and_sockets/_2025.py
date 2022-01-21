'''_2025.py

MountableComponentOuterSocket
'''


from mastapy.system_model.connections_and_sockets import _2026
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_OUTER_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'MountableComponentOuterSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentOuterSocket',)


class MountableComponentOuterSocket(_2026.MountableComponentSocket):
    '''MountableComponentOuterSocket

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_OUTER_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentOuterSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
