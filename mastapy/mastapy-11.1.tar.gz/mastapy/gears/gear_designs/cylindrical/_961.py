'''_961.py

CrossedAxisCylindricalGearPairLineContact
'''


from mastapy.gears.gear_designs.cylindrical import _960
from mastapy._internal.python_net import python_net_import

_CROSSED_AXIS_CYLINDRICAL_GEAR_PAIR_LINE_CONTACT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CrossedAxisCylindricalGearPairLineContact')


__docformat__ = 'restructuredtext en'
__all__ = ('CrossedAxisCylindricalGearPairLineContact',)


class CrossedAxisCylindricalGearPairLineContact(_960.CrossedAxisCylindricalGearPair):
    '''CrossedAxisCylindricalGearPairLineContact

    This is a mastapy class.
    '''

    TYPE = _CROSSED_AXIS_CYLINDRICAL_GEAR_PAIR_LINE_CONTACT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CrossedAxisCylindricalGearPairLineContact.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
