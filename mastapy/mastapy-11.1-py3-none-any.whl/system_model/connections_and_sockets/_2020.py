'''_2020.py

ElectricMachineStatorSocket
'''


from mastapy.system_model.connections_and_sockets import _2038
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_STATOR_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'ElectricMachineStatorSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineStatorSocket',)


class ElectricMachineStatorSocket(_2038.Socket):
    '''ElectricMachineStatorSocket

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_STATOR_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineStatorSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
