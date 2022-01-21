'''_2084.py

ClutchConnection
'''


from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets.couplings import _2088
from mastapy._internal.python_net import python_net_import

_CLUTCH_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'ClutchConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchConnection',)


class ClutchConnection(_2088.CouplingConnection):
    '''ClutchConnection

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def torque_capacity(self) -> 'float':
        '''float: 'TorqueCapacity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueCapacity

    @property
    def effective_torque_radius(self) -> 'float':
        '''float: 'EffectiveTorqueRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveTorqueRadius
