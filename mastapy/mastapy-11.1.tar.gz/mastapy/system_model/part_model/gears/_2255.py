'''_2255.py

BevelDifferentialGear
'''


from mastapy.gears.gear_designs.bevel import _1127
from mastapy._internal import constructor
from mastapy.gears.gear_designs.zerol_bevel import _909
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.straight_bevel_diff import _918
from mastapy.gears.gear_designs.straight_bevel import _922
from mastapy.gears.gear_designs.spiral_bevel import _926
from mastapy.system_model.part_model.gears import _2259
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialGear')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGear',)


class BevelDifferentialGear(_2259.BevelGear):
    '''BevelDifferentialGear

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bevel_gear_design(self) -> '_1127.BevelGearDesign':
        '''BevelGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1127.BevelGearDesign.TYPE not in self.wrapped.BevelGearDesign.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_design to BevelGearDesign. Expected: {}.'.format(self.wrapped.BevelGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearDesign.__class__)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None

    @property
    def bevel_gear_design_of_type_zerol_bevel_gear_design(self) -> '_909.ZerolBevelGearDesign':
        '''ZerolBevelGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _909.ZerolBevelGearDesign.TYPE not in self.wrapped.BevelGearDesign.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_design to ZerolBevelGearDesign. Expected: {}.'.format(self.wrapped.BevelGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearDesign.__class__)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None

    @property
    def bevel_gear_design_of_type_straight_bevel_diff_gear_design(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _918.StraightBevelDiffGearDesign.TYPE not in self.wrapped.BevelGearDesign.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_design to StraightBevelDiffGearDesign. Expected: {}.'.format(self.wrapped.BevelGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearDesign.__class__)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None

    @property
    def bevel_gear_design_of_type_straight_bevel_gear_design(self) -> '_922.StraightBevelGearDesign':
        '''StraightBevelGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _922.StraightBevelGearDesign.TYPE not in self.wrapped.BevelGearDesign.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_design to StraightBevelGearDesign. Expected: {}.'.format(self.wrapped.BevelGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearDesign.__class__)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None

    @property
    def bevel_gear_design_of_type_spiral_bevel_gear_design(self) -> '_926.SpiralBevelGearDesign':
        '''SpiralBevelGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _926.SpiralBevelGearDesign.TYPE not in self.wrapped.BevelGearDesign.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_design to SpiralBevelGearDesign. Expected: {}.'.format(self.wrapped.BevelGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearDesign.__class__)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None
