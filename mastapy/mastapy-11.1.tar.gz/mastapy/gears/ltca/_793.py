'''_793.py

GearBendingStiffness
'''


from mastapy.gears.ltca import _807
from mastapy._internal.python_net import python_net_import

_GEAR_BENDING_STIFFNESS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearBendingStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('GearBendingStiffness',)


class GearBendingStiffness(_807.GearStiffness):
    '''GearBendingStiffness

    This is a mastapy class.
    '''

    TYPE = _GEAR_BENDING_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearBendingStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
