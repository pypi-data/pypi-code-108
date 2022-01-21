'''_1096.py

SpiralBevelGearSetCreationOptions
'''


from mastapy.gears.gear_designs.creation_options import _1094
from mastapy.gears.gear_designs.spiral_bevel import _928
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.CreationOptions', 'SpiralBevelGearSetCreationOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetCreationOptions',)


class SpiralBevelGearSetCreationOptions(_1094.GearSetCreationOptions['_928.SpiralBevelGearSetDesign']):
    '''SpiralBevelGearSetCreationOptions

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_CREATION_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetCreationOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
