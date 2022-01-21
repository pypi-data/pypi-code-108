'''_2089.py

CouplingSocket
'''


from mastapy.system_model.connections_and_sockets import _2018
from mastapy._internal.python_net import python_net_import

_COUPLING_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'CouplingSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingSocket',)


class CouplingSocket(_2018.CylindricalSocket):
    '''CouplingSocket

    This is a mastapy class.
    '''

    TYPE = _COUPLING_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
