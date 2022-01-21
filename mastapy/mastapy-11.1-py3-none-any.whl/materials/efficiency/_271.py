'''_271.py

ResistiveTorque
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RESISTIVE_TORQUE = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'ResistiveTorque')


__docformat__ = 'restructuredtext en'
__all__ = ('ResistiveTorque',)


class ResistiveTorque(_0.APIBase):
    '''ResistiveTorque

    This is a mastapy class.
    '''

    TYPE = _RESISTIVE_TORQUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResistiveTorque.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def total_resistive_torque(self) -> 'float':
        '''float: 'TotalResistiveTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalResistiveTorque
