'''_2072.py

WormGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2056
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'WormGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearTeethSocket',)


class WormGearTeethSocket(_2056.GearTeethSocket):
    '''WormGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
