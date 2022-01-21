'''_1120.py

ConicalGearFlankMicroGeometry
'''


from mastapy.gears import _302
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.gear_designs.conical.micro_geometry import _1122, _1121, _1119
from mastapy.gears.gear_designs.conical import _1101
from mastapy.gears.gear_designs.zerol_bevel import _909
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.straight_bevel_diff import _918
from mastapy.gears.gear_designs.straight_bevel import _922
from mastapy.gears.gear_designs.spiral_bevel import _926
from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _930
from mastapy.gears.gear_designs.klingelnberg_hypoid import _934
from mastapy.gears.gear_designs.klingelnberg_conical import _938
from mastapy.gears.gear_designs.hypoid import _942
from mastapy.gears.gear_designs.bevel import _1127
from mastapy.gears.gear_designs.agma_gleason_conical import _1140
from mastapy.gears.micro_geometry import _530
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_FLANK_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical.MicroGeometry', 'ConicalGearFlankMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearFlankMicroGeometry',)


class ConicalGearFlankMicroGeometry(_530.FlankMicroGeometry):
    '''ConicalGearFlankMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_FLANK_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearFlankMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def micro_geometry_input_type(self) -> '_302.MicroGeometryInputTypes':
        '''MicroGeometryInputTypes: 'MicroGeometryInputType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MicroGeometryInputType)
        return constructor.new(_302.MicroGeometryInputTypes)(value) if value is not None else None

    @micro_geometry_input_type.setter
    def micro_geometry_input_type(self, value: '_302.MicroGeometryInputTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MicroGeometryInputType = value

    @property
    def profile_relief(self) -> '_1122.ConicalGearProfileModification':
        '''ConicalGearProfileModification: 'ProfileRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1122.ConicalGearProfileModification)(self.wrapped.ProfileRelief) if self.wrapped.ProfileRelief is not None else None

    @property
    def lead_relief(self) -> '_1121.ConicalGearLeadModification':
        '''ConicalGearLeadModification: 'LeadRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1121.ConicalGearLeadModification)(self.wrapped.LeadRelief) if self.wrapped.LeadRelief is not None else None

    @property
    def bias(self) -> '_1119.ConicalGearBiasModification':
        '''ConicalGearBiasModification: 'Bias' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1119.ConicalGearBiasModification)(self.wrapped.Bias) if self.wrapped.Bias is not None else None

    @property
    def gear_design(self) -> '_1101.ConicalGearDesign':
        '''ConicalGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1101.ConicalGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to ConicalGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_zerol_bevel_gear_design(self) -> '_909.ZerolBevelGearDesign':
        '''ZerolBevelGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _909.ZerolBevelGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to ZerolBevelGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_straight_bevel_diff_gear_design(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _918.StraightBevelDiffGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to StraightBevelDiffGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_straight_bevel_gear_design(self) -> '_922.StraightBevelGearDesign':
        '''StraightBevelGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _922.StraightBevelGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to StraightBevelGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_spiral_bevel_gear_design(self) -> '_926.SpiralBevelGearDesign':
        '''SpiralBevelGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _926.SpiralBevelGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to SpiralBevelGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_design(self) -> '_930.KlingelnbergCycloPalloidSpiralBevelGearDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _930.KlingelnbergCycloPalloidSpiralBevelGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to KlingelnbergCycloPalloidSpiralBevelGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear_design(self) -> '_934.KlingelnbergCycloPalloidHypoidGearDesign':
        '''KlingelnbergCycloPalloidHypoidGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _934.KlingelnbergCycloPalloidHypoidGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to KlingelnbergCycloPalloidHypoidGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_klingelnberg_conical_gear_design(self) -> '_938.KlingelnbergConicalGearDesign':
        '''KlingelnbergConicalGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _938.KlingelnbergConicalGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to KlingelnbergConicalGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_hypoid_gear_design(self) -> '_942.HypoidGearDesign':
        '''HypoidGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _942.HypoidGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to HypoidGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_bevel_gear_design(self) -> '_1127.BevelGearDesign':
        '''BevelGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1127.BevelGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to BevelGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def gear_design_of_type_agma_gleason_conical_gear_design(self) -> '_1140.AGMAGleasonConicalGearDesign':
        '''AGMAGleasonConicalGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1140.AGMAGleasonConicalGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to AGMAGleasonConicalGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None
