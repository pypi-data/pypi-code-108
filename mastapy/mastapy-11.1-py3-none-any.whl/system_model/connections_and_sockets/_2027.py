'''_2027.py

OuterShaftSocket
'''


from mastapy.system_model.connections_and_sockets import _2028
from mastapy._internal.python_net import python_net_import

_OUTER_SHAFT_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'OuterShaftSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('OuterShaftSocket',)


class OuterShaftSocket(_2028.OuterShaftSocketBase):
    '''OuterShaftSocket

    This is a mastapy class.
    '''

    TYPE = _OUTER_SHAFT_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OuterShaftSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
