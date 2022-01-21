'''_2042.py

AGMAGleasonConicalGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2050
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'AGMAGleasonConicalGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearTeethSocket',)


class AGMAGleasonConicalGearTeethSocket(_2050.ConicalGearTeethSocket):
    '''AGMAGleasonConicalGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
