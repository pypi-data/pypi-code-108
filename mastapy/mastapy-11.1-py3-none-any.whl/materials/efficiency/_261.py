'''_261.py

CombinedResistiveTorque
'''


from mastapy.materials.efficiency import _271
from mastapy._internal.python_net import python_net_import

_COMBINED_RESISTIVE_TORQUE = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'CombinedResistiveTorque')


__docformat__ = 'restructuredtext en'
__all__ = ('CombinedResistiveTorque',)


class CombinedResistiveTorque(_271.ResistiveTorque):
    '''CombinedResistiveTorque

    This is a mastapy class.
    '''

    TYPE = _COMBINED_RESISTIVE_TORQUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CombinedResistiveTorque.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
