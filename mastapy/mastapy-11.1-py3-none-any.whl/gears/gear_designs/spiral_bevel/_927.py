'''_927.py

SpiralBevelGearMeshDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.spiral_bevel import _928, _926, _929
from mastapy.gears.gear_designs.bevel import _1128
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.SpiralBevel', 'SpiralBevelGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearMeshDesign',)


class SpiralBevelGearMeshDesign(_1128.BevelGearMeshDesign):
    '''SpiralBevelGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearMeshDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def wheel_inner_blade_angle_convex(self) -> 'float':
        '''float: 'WheelInnerBladeAngleConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInnerBladeAngleConvex

    @property
    def wheel_outer_blade_angle_concave(self) -> 'float':
        '''float: 'WheelOuterBladeAngleConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelOuterBladeAngleConcave

    @property
    def spiral_bevel_gear_set(self) -> '_928.SpiralBevelGearSetDesign':
        '''SpiralBevelGearSetDesign: 'SpiralBevelGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_928.SpiralBevelGearSetDesign)(self.wrapped.SpiralBevelGearSet) if self.wrapped.SpiralBevelGearSet is not None else None

    @property
    def spiral_bevel_gears(self) -> 'List[_926.SpiralBevelGearDesign]':
        '''List[SpiralBevelGearDesign]: 'SpiralBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGears, constructor.new(_926.SpiralBevelGearDesign))
        return value

    @property
    def spiral_bevel_meshed_gears(self) -> 'List[_929.SpiralBevelMeshedGearDesign]':
        '''List[SpiralBevelMeshedGearDesign]: 'SpiralBevelMeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelMeshedGears, constructor.new(_929.SpiralBevelMeshedGearDesign))
        return value
