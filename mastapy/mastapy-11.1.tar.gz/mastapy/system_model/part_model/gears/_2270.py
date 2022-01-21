'''_2270.py

Gear
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs import _904
from mastapy.gears.gear_designs.zerol_bevel import _909
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.worm import _913, _914, _917
from mastapy.gears.gear_designs.straight_bevel_diff import _918
from mastapy.gears.gear_designs.straight_bevel import _922
from mastapy.gears.gear_designs.spiral_bevel import _926
from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _930
from mastapy.gears.gear_designs.klingelnberg_hypoid import _934
from mastapy.gears.gear_designs.klingelnberg_conical import _938
from mastapy.gears.gear_designs.hypoid import _942
from mastapy.gears.gear_designs.face import _946, _951, _954
from mastapy.gears.gear_designs.cylindrical import _969, _996
from mastapy.gears.gear_designs.conical import _1101
from mastapy.gears.gear_designs.concept import _1123
from mastapy.gears.gear_designs.bevel import _1127
from mastapy.gears.gear_designs.agma_gleason_conical import _1140
from mastapy.system_model.part_model.gears import (
    _2272, _2254, _2256, _2260,
    _2262, _2264, _2266, _2269,
    _2275, _2277, _2279, _2281,
    _2282, _2284, _2286, _2288,
    _2292, _2294
)
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model import _2205
from mastapy._internal.python_net import python_net_import

_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'Gear')


__docformat__ = 'restructuredtext en'
__all__ = ('Gear',)


class Gear(_2205.MountableComponent):
    '''Gear

    This is a mastapy class.
    '''

    TYPE = _GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Gear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_clone_gear(self) -> 'bool':
        '''bool: 'IsCloneGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsCloneGear

    @property
    def cloned_from(self) -> 'str':
        '''str: 'ClonedFrom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClonedFrom

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def maximum_number_of_teeth(self) -> 'int':
        '''int: 'MaximumNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfTeeth

    @maximum_number_of_teeth.setter
    def maximum_number_of_teeth(self, value: 'int'):
        self.wrapped.MaximumNumberOfTeeth = int(value) if value else 0

    @property
    def minimum_number_of_teeth(self) -> 'int':
        '''int: 'MinimumNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.MinimumNumberOfTeeth

    @minimum_number_of_teeth.setter
    def minimum_number_of_teeth(self, value: 'int'):
        self.wrapped.MinimumNumberOfTeeth = int(value) if value else 0

    @property
    def active_gear_design(self) -> '_904.GearDesign':
        '''GearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _904.GearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to GearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_zerol_bevel_gear_design(self) -> '_909.ZerolBevelGearDesign':
        '''ZerolBevelGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _909.ZerolBevelGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to ZerolBevelGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_worm_design(self) -> '_913.WormDesign':
        '''WormDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _913.WormDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to WormDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_worm_gear_design(self) -> '_914.WormGearDesign':
        '''WormGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _914.WormGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to WormGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_worm_wheel_design(self) -> '_917.WormWheelDesign':
        '''WormWheelDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _917.WormWheelDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to WormWheelDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_straight_bevel_diff_gear_design(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _918.StraightBevelDiffGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to StraightBevelDiffGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_straight_bevel_gear_design(self) -> '_922.StraightBevelGearDesign':
        '''StraightBevelGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _922.StraightBevelGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to StraightBevelGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_spiral_bevel_gear_design(self) -> '_926.SpiralBevelGearDesign':
        '''SpiralBevelGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _926.SpiralBevelGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to SpiralBevelGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_design(self) -> '_930.KlingelnbergCycloPalloidSpiralBevelGearDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _930.KlingelnbergCycloPalloidSpiralBevelGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to KlingelnbergCycloPalloidSpiralBevelGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear_design(self) -> '_934.KlingelnbergCycloPalloidHypoidGearDesign':
        '''KlingelnbergCycloPalloidHypoidGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _934.KlingelnbergCycloPalloidHypoidGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to KlingelnbergCycloPalloidHypoidGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_klingelnberg_conical_gear_design(self) -> '_938.KlingelnbergConicalGearDesign':
        '''KlingelnbergConicalGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _938.KlingelnbergConicalGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to KlingelnbergConicalGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_hypoid_gear_design(self) -> '_942.HypoidGearDesign':
        '''HypoidGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _942.HypoidGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to HypoidGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_face_gear_design(self) -> '_946.FaceGearDesign':
        '''FaceGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _946.FaceGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to FaceGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_face_gear_pinion_design(self) -> '_951.FaceGearPinionDesign':
        '''FaceGearPinionDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _951.FaceGearPinionDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to FaceGearPinionDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_face_gear_wheel_design(self) -> '_954.FaceGearWheelDesign':
        '''FaceGearWheelDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _954.FaceGearWheelDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to FaceGearWheelDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_cylindrical_gear_design(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_cylindrical_planet_gear_design(self) -> '_996.CylindricalPlanetGearDesign':
        '''CylindricalPlanetGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _996.CylindricalPlanetGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to CylindricalPlanetGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_conical_gear_design(self) -> '_1101.ConicalGearDesign':
        '''ConicalGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1101.ConicalGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to ConicalGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_concept_gear_design(self) -> '_1123.ConceptGearDesign':
        '''ConceptGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1123.ConceptGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to ConceptGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_bevel_gear_design(self) -> '_1127.BevelGearDesign':
        '''BevelGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1127.BevelGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to BevelGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def active_gear_design_of_type_agma_gleason_conical_gear_design(self) -> '_1140.AGMAGleasonConicalGearDesign':
        '''AGMAGleasonConicalGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1140.AGMAGleasonConicalGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to AGMAGleasonConicalGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def gear_set(self) -> '_2272.GearSet':
        '''GearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2272.GearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to GearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_agma_gleason_conical_gear_set(self) -> '_2254.AGMAGleasonConicalGearSet':
        '''AGMAGleasonConicalGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2254.AGMAGleasonConicalGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to AGMAGleasonConicalGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_bevel_differential_gear_set(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2256.BevelDifferentialGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to BevelDifferentialGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_bevel_gear_set(self) -> '_2260.BevelGearSet':
        '''BevelGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2260.BevelGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to BevelGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_concept_gear_set(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2262.ConceptGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to ConceptGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_conical_gear_set(self) -> '_2264.ConicalGearSet':
        '''ConicalGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2264.ConicalGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to ConicalGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_cylindrical_gear_set(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to CylindricalGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_face_gear_set(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2269.FaceGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to FaceGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_hypoid_gear_set(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2275.HypoidGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to HypoidGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        '''KlingelnbergCycloPalloidConicalGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2277.KlingelnbergCycloPalloidConicalGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to KlingelnbergCycloPalloidConicalGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to KlingelnbergCycloPalloidHypoidGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to KlingelnbergCycloPalloidSpiralBevelGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_planetary_gear_set(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2282.PlanetaryGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to PlanetaryGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_spiral_bevel_gear_set(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2284.SpiralBevelGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to SpiralBevelGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_straight_bevel_diff_gear_set(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2286.StraightBevelDiffGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to StraightBevelDiffGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_straight_bevel_gear_set(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2288.StraightBevelGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to StraightBevelGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_worm_gear_set(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2292.WormGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to WormGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def gear_set_of_type_zerol_bevel_gear_set(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'GearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2294.ZerolBevelGearSet.TYPE not in self.wrapped.GearSet.__class__.__mro__:
            raise CastException('Failed to cast gear_set to ZerolBevelGearSet. Expected: {}.'.format(self.wrapped.GearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSet.__class__)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def number_of_teeth(self) -> 'int':
        '''int: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'int'):
        self.wrapped.NumberOfTeeth = int(value) if value else 0

    @property
    def shaft(self) -> '_2223.Shaft':
        '''Shaft: 'Shaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.Shaft) if self.wrapped.Shaft is not None else None

    def connect_to(self, other_gear: 'Gear'):
        ''' 'ConnectTo' is the original name of this method.

        Args:
            other_gear (mastapy.system_model.part_model.gears.Gear)
        '''

        self.wrapped.ConnectTo(other_gear.wrapped if other_gear else None)
