'''_2023.py

InterMountableComponentConnection
'''


from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets import _2014
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'InterMountableComponentConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnection',)


class InterMountableComponentConnection(_2014.Connection):
    '''InterMountableComponentConnection

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def additional_modal_damping_ratio(self) -> 'float':
        '''float: 'AdditionalModalDampingRatio' is the original name of this property.'''

        return self.wrapped.AdditionalModalDampingRatio

    @additional_modal_damping_ratio.setter
    def additional_modal_damping_ratio(self, value: 'float'):
        self.wrapped.AdditionalModalDampingRatio = float(value) if value else 0.0
