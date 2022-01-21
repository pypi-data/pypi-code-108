'''_2038.py

Socket
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import (
    _2186, _2178, _2179, _2182,
    _2184, _2189, _2190, _2193,
    _2194, _2196, _2203, _2204,
    _2205, _2207, _2210, _2212,
    _2213, _2218, _2220, _2187
)
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.gears import (
    _2253, _2255, _2257, _2258,
    _2259, _2261, _2263, _2265,
    _2267, _2268, _2270, _2274,
    _2276, _2278, _2280, _2283,
    _2285, _2287, _2289, _2290,
    _2291, _2293
)
from mastapy.system_model.part_model.cycloidal import _2309, _2310
from mastapy.system_model.part_model.couplings import (
    _2319, _2322, _2324, _2327,
    _2329, _2330, _2336, _2338,
    _2341, _2344, _2345, _2346,
    _2348, _2350
)
from mastapy.system_model.connections_and_sockets import _2014
from mastapy._internal.python_net import python_net_import
from mastapy import _0

_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'Socket')
_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Component')


__docformat__ = 'restructuredtext en'
__all__ = ('Socket',)


class Socket(_0.APIBase):
    '''Socket

    This is a mastapy class.
    '''

    TYPE = _SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Socket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def owner(self) -> '_2186.Component':
        '''Component: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.Component.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Component. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AbstractShaft. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Bearing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.Bolt.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Bolt. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Connector. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.Datum.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Datum. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2193.ExternalCADModel.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ExternalCADModel. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to FEPart. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.GuideDxfModel.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to GuideDxfModel. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MassDisc. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MeasurementComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to MountableComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to OilSeal. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PlanetCarrier. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PointLoad. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PowerLoad. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to UnbalancedMass. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to VirtualComponent. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Shaft. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to BevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConceptGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CylindricalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to FaceGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Gear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to HypoidGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SpiralBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to WormGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ZerolBevelGear. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CycloidalDisc. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to RingPins. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ClutchHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to CVTPulley. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to Pulley. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to RollingRing. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to ShaftHubConnection. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SpringDamperHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserHalf. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserPart. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to TorqueConverterPump. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def owner_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'Owner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.Owner.__class__.__mro__:
            raise CastException('Failed to cast owner to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.Owner.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Owner.__class__)(self.wrapped.Owner) if self.wrapped.Owner is not None else None

    @property
    def connections(self) -> 'List[_2014.Connection]':
        '''List[Connection]: 'Connections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Connections, constructor.new(_2014.Connection))
        return value

    @property
    def connected_components(self) -> 'List[_2186.Component]':
        '''List[Component]: 'ConnectedComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectedComponents, constructor.new(_2186.Component))
        return value

    def connect_to_socket(self, socket: 'Socket') -> '_2187.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_SOCKET](socket.wrapped if socket else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_possible_sockets_to_connect_to(self, component_to_connect_to: '_2186.Component') -> 'List[Socket]':
        ''' 'GetPossibleSocketsToConnectTo' is the original name of this method.

        Args:
            component_to_connect_to (mastapy.system_model.part_model.Component)

        Returns:
            List[mastapy.system_model.connections_and_sockets.Socket]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetPossibleSocketsToConnectTo(component_to_connect_to.wrapped if component_to_connect_to else None), constructor.new(Socket))

    def connect_to(self, component: '_2186.Component') -> '_2187.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_COMPONENT](component.wrapped if component else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def connection_to(self, socket: 'Socket') -> '_2014.Connection':
        ''' 'ConnectionTo' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            mastapy.system_model.connections_and_sockets.Connection
        '''

        method_result = self.wrapped.ConnectionTo(socket.wrapped if socket else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
