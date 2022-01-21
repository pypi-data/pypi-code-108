'''_2059.py

KlingelnbergConicalGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2050
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CONICAL_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergConicalGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalGearTeethSocket',)


class KlingelnbergConicalGearTeethSocket(_2050.ConicalGearTeethSocket):
    '''KlingelnbergConicalGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
