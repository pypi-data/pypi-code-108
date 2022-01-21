'''_920.py

StraightBevelDiffGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.straight_bevel_diff import _918, _919
from mastapy.gears.gear_designs.bevel import _1129
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.StraightBevelDiff', 'StraightBevelDiffGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearSetDesign',)


class StraightBevelDiffGearSetDesign(_1129.BevelGearSetDesign):
    '''StraightBevelDiffGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def derating_factor(self) -> 'float':
        '''float: 'DeratingFactor' is the original name of this property.'''

        return self.wrapped.DeratingFactor

    @derating_factor.setter
    def derating_factor(self, value: 'float'):
        self.wrapped.DeratingFactor = float(value) if value else 0.0

    @property
    def gears(self) -> 'List[_918.StraightBevelDiffGearDesign]':
        '''List[StraightBevelDiffGearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_918.StraightBevelDiffGearDesign))
        return value

    @property
    def straight_bevel_diff_gears(self) -> 'List[_918.StraightBevelDiffGearDesign]':
        '''List[StraightBevelDiffGearDesign]: 'StraightBevelDiffGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGears, constructor.new(_918.StraightBevelDiffGearDesign))
        return value

    @property
    def straight_bevel_diff_meshes(self) -> 'List[_919.StraightBevelDiffGearMeshDesign]':
        '''List[StraightBevelDiffGearMeshDesign]: 'StraightBevelDiffMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffMeshes, constructor.new(_919.StraightBevelDiffGearMeshDesign))
        return value
