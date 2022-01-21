'''_2063.py

KlingelnbergHypoidGearTeethSocket
'''


from mastapy.system_model.connections_and_sockets.gears import _2059
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_HYPOID_GEAR_TEETH_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergHypoidGearTeethSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergHypoidGearTeethSocket',)


class KlingelnbergHypoidGearTeethSocket(_2059.KlingelnbergConicalGearTeethSocket):
    '''KlingelnbergHypoidGearTeethSocket

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_HYPOID_GEAR_TEETH_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergHypoidGearTeethSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
