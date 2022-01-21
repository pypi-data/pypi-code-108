'''_2037.py

ShaftToMountableComponentConnection
'''


from mastapy.system_model.connections_and_sockets import _2007
from mastapy._internal.python_net import python_net_import

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'ShaftToMountableComponentConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftToMountableComponentConnection',)


class ShaftToMountableComponentConnection(_2007.AbstractShaftToMountableComponentConnection):
    '''ShaftToMountableComponentConnection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftToMountableComponentConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
