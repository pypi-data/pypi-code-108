'''_2032.py

PulleySocket
'''


from mastapy.system_model.connections_and_sockets import _2018
from mastapy._internal.python_net import python_net_import

_PULLEY_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'PulleySocket')


__docformat__ = 'restructuredtext en'
__all__ = ('PulleySocket',)


class PulleySocket(_2018.CylindricalSocket):
    '''PulleySocket

    This is a mastapy class.
    '''

    TYPE = _PULLEY_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PulleySocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
