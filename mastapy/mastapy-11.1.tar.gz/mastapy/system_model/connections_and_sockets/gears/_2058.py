'''_2058.py

HypoidGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2042
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'HypoidGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearTeethSocket',)


class HypoidGearTeethSocket(_2042.AGMAGleasonConicalGearTeethSocket):
    '''HypoidGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
