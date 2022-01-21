'''_2007.py

AbstractShaftToMountableComponentConnection
'''


from mastapy.system_model.part_model import (
    _2205, _2182, _2189, _2203,
    _2204, _2207, _2210, _2212,
    _2213, _2218, _2220, _2178
)
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.gears import (
    _2253, _2255, _2257, _2258,
    _2259, _2261, _2263, _2265,
    _2267, _2268, _2270, _2274,
    _2276, _2278, _2280, _2283,
    _2285, _2287, _2289, _2290,
    _2291, _2293
)
from mastapy.system_model.part_model.cycloidal import _2310, _2309
from mastapy.system_model.part_model.couplings import (
    _2319, _2322, _2324, _2327,
    _2329, _2330, _2336, _2338,
    _2341, _2344, _2345, _2346,
    _2348, _2350
)
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.connections_and_sockets import _2014
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'AbstractShaftToMountableComponentConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnection',)


class AbstractShaftToMountableComponentConnection(_2014.Connection):
    '''AbstractShaftToMountableComponentConnection

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to MountableComponent. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to Bearing. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to Connector. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to MassDisc. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to MeasurementComponent. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to OilSeal. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to PlanetCarrier. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to PointLoad. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to PowerLoad. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to UnbalancedMass. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to VirtualComponent. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to BevelGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ConceptGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ConicalGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to CylindricalGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to FaceGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to Gear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to HypoidGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to SpiralBevelGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to StraightBevelGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to WormGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ZerolBevelGear. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to RingPins. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ClutchHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to CouplingHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to CVTPulley. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to Pulley. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to RollingRing. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to ShaftHubConnection. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to SpringDamperHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to SynchroniserHalf. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to SynchroniserPart. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to TorqueConverterPump. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def mountable_component_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'MountableComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.MountableComponent.__class__.__mro__:
            raise CastException('Failed to cast mountable_component to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.MountableComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MountableComponent.__class__)(self.wrapped.MountableComponent) if self.wrapped.MountableComponent is not None else None

    @property
    def shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'Shaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.Shaft.__class__.__mro__:
            raise CastException('Failed to cast shaft to AbstractShaft. Expected: {}.'.format(self.wrapped.Shaft.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Shaft.__class__)(self.wrapped.Shaft) if self.wrapped.Shaft is not None else None

    @property
    def shaft_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'Shaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.Shaft.__class__.__mro__:
            raise CastException('Failed to cast shaft to Shaft. Expected: {}.'.format(self.wrapped.Shaft.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Shaft.__class__)(self.wrapped.Shaft) if self.wrapped.Shaft is not None else None

    @property
    def shaft_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'Shaft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.Shaft.__class__.__mro__:
            raise CastException('Failed to cast shaft to CycloidalDisc. Expected: {}.'.format(self.wrapped.Shaft.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Shaft.__class__)(self.wrapped.Shaft) if self.wrapped.Shaft is not None else None
