'''_962.py

CrossedAxisCylindricalGearPairPointContact
'''


from mastapy.gears.gear_designs.cylindrical import _960
from mastapy._internal.python_net import python_net_import

_CROSSED_AXIS_CYLINDRICAL_GEAR_PAIR_POINT_CONTACT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CrossedAxisCylindricalGearPairPointContact')


__docformat__ = 'restructuredtext en'
__all__ = ('CrossedAxisCylindricalGearPairPointContact',)


class CrossedAxisCylindricalGearPairPointContact(_960.CrossedAxisCylindricalGearPair):
    '''CrossedAxisCylindricalGearPairPointContact

    This is a mastapy class.
    '''

    TYPE = _CROSSED_AXIS_CYLINDRICAL_GEAR_PAIR_POINT_CONTACT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CrossedAxisCylindricalGearPairPointContact.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
