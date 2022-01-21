'''_2070.py

StraightBevelGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2046
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'StraightBevelGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearTeethSocket',)


class StraightBevelGearTeethSocket(_2046.BevelGearTeethSocket):
    '''StraightBevelGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
