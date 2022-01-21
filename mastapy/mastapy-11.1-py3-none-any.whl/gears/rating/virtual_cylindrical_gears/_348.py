'''_348.py

HypoidVirtualCylindricalGearSetISO10300MethodB1
'''


from mastapy.gears.rating.virtual_cylindrical_gears import _359
from mastapy._internal.python_net import python_net_import

_HYPOID_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B1 = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'HypoidVirtualCylindricalGearSetISO10300MethodB1')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidVirtualCylindricalGearSetISO10300MethodB1',)


class HypoidVirtualCylindricalGearSetISO10300MethodB1(_359.VirtualCylindricalGearSetISO10300MethodB1):
    '''HypoidVirtualCylindricalGearSetISO10300MethodB1

    This is a mastapy class.
    '''

    TYPE = _HYPOID_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B1

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidVirtualCylindricalGearSetISO10300MethodB1.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
