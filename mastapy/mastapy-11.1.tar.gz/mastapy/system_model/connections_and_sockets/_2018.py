'''_2018.py

CylindricalSocket
'''


from mastapy.system_model.connections_and_sockets import _2038
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'CylindricalSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalSocket',)


class CylindricalSocket(_2038.Socket):
    '''CylindricalSocket

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
