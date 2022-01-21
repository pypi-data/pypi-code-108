'''_2079.py

CycloidalDiscOuterSocket
'''


from mastapy.system_model.connections_and_sockets import _2018
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_OUTER_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscOuterSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscOuterSocket',)


class CycloidalDiscOuterSocket(_2018.CylindricalSocket):
    '''CycloidalDiscOuterSocket

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_OUTER_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscOuterSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
