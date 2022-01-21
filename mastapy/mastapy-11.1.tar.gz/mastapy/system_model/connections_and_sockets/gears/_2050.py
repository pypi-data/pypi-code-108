'''_2050.py

ConicalGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2056
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'ConicalGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearTeethSocket',)


class ConicalGearTeethSocket(_2056.GearTeethSocket):
    '''ConicalGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
