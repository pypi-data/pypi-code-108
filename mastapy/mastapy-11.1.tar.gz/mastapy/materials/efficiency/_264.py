'''_264.py

IndependentResistiveTorque
'''


from mastapy._internal import constructor
from mastapy.materials.efficiency import _271
from mastapy._internal.python_net import python_net_import

_INDEPENDENT_RESISTIVE_TORQUE = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'IndependentResistiveTorque')


__docformat__ = 'restructuredtext en'
__all__ = ('IndependentResistiveTorque',)


class IndependentResistiveTorque(_271.ResistiveTorque):
    '''IndependentResistiveTorque

    This is a mastapy class.
    '''

    TYPE = _INDEPENDENT_RESISTIVE_TORQUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'IndependentResistiveTorque.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_dependent_resistive_torque(self) -> 'float':
        '''float: 'LoadDependentResistiveTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDependentResistiveTorque

    @property
    def speed_dependent_resistive_torque(self) -> 'float':
        '''float: 'SpeedDependentResistiveTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpeedDependentResistiveTorque
