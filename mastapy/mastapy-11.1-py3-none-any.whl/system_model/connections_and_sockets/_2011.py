'''_2011.py

CoaxialConnection
'''


from mastapy.system_model.connections_and_sockets import _2037
from mastapy._internal.python_net import python_net_import

_COAXIAL_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'CoaxialConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('CoaxialConnection',)


class CoaxialConnection(_2037.ShaftToMountableComponentConnection):
    '''CoaxialConnection

    This is a mastapy class.
    '''

    TYPE = _COAXIAL_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CoaxialConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
