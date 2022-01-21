'''_346.py

BevelVirtualCylindricalGearSetISO10300MethodB2
'''


from mastapy.gears.rating.virtual_cylindrical_gears import _360
from mastapy._internal.python_net import python_net_import

_BEVEL_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'BevelVirtualCylindricalGearSetISO10300MethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelVirtualCylindricalGearSetISO10300MethodB2',)


class BevelVirtualCylindricalGearSetISO10300MethodB2(_360.VirtualCylindricalGearSetISO10300MethodB2):
    '''BevelVirtualCylindricalGearSetISO10300MethodB2

    This is a mastapy class.
    '''

    TYPE = _BEVEL_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelVirtualCylindricalGearSetISO10300MethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
