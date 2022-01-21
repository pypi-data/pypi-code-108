'''_928.py

SpiralBevelGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.spiral_bevel import _926, _927
from mastapy.gears.gear_designs.bevel import _1129
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.SpiralBevel', 'SpiralBevelGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSetDesign',)


class SpiralBevelGearSetDesign(_1129.BevelGearSetDesign):
    '''SpiralBevelGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_number_of_teeth_for_recommended_tooth_proportions(self) -> 'int':
        '''int: 'MinimumNumberOfTeethForRecommendedToothProportions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumNumberOfTeethForRecommendedToothProportions

    @property
    def gears(self) -> 'List[_926.SpiralBevelGearDesign]':
        '''List[SpiralBevelGearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_926.SpiralBevelGearDesign))
        return value

    @property
    def spiral_bevel_gears(self) -> 'List[_926.SpiralBevelGearDesign]':
        '''List[SpiralBevelGearDesign]: 'SpiralBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGears, constructor.new(_926.SpiralBevelGearDesign))
        return value

    @property
    def spiral_bevel_meshes(self) -> 'List[_927.SpiralBevelGearMeshDesign]':
        '''List[SpiralBevelGearMeshDesign]: 'SpiralBevelMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshes, constructor.new(_927.SpiralBevelGearMeshDesign))
        return value
