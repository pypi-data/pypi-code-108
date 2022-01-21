'''_2021.py

InnerShaftSocket
'''


from mastapy.system_model.connections_and_sockets import _2022
from mastapy._internal.python_net import python_net_import

_INNER_SHAFT_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'InnerShaftSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('InnerShaftSocket',)


class InnerShaftSocket(_2022.InnerShaftSocketBase):
    '''InnerShaftSocket

    This is a mastapy class.
    '''

    TYPE = _INNER_SHAFT_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InnerShaftSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
