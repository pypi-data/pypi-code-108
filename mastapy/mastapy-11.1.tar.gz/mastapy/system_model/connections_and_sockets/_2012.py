'''_2012.py

ComponentConnection
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import (
    _2186, _2178, _2179, _2182,
    _2184, _2189, _2190, _2193,
    _2194, _2196, _2203, _2204,
    _2205, _2207, _2210, _2212,
    _2213, _2218, _2220
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
from mastapy.system_model.connections_and_sockets import _2013
from mastapy._internal.python_net import python_net_import

_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'ComponentConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentConnection',)


class ComponentConnection(_2013.ComponentMeasurer):
    '''ComponentConnection

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def socket(self) -> 'str':
        '''str: 'Socket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Socket

    @property
    def connected_components_socket(self) -> 'str':
        '''str: 'ConnectedComponentsSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConnectedComponentsSocket

    @property
    def assembly_view(self) -> 'Image':
        '''Image: 'AssemblyView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.AssemblyView)
        return value

    @property
    def detail_view(self) -> 'Image':
        '''Image: 'DetailView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.DetailView)
        return value

    @property
    def connected_component(self) -> '_2186.Component':
        '''Component: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.Component.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Component. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to AbstractShaft. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Bearing. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.Bolt.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Bolt. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Connector. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.Datum.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Datum. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2193.ExternalCADModel.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ExternalCADModel. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to FEPart. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.GuideDxfModel.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to GuideDxfModel. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to MassDisc. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to MeasurementComponent. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to MountableComponent. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to OilSeal. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to PlanetCarrier. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to PointLoad. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to PowerLoad. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to UnbalancedMass. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to VirtualComponent. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Shaft. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to BevelGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ConceptGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ConicalGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to CylindricalGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to FaceGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Gear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to HypoidGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to SpiralBevelGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to StraightBevelGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to WormGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ZerolBevelGear. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to CycloidalDisc. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to RingPins. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ClutchHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to CouplingHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to CVTPulley. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to Pulley. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to RollingRing. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to ShaftHubConnection. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to SpringDamperHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to SynchroniserHalf. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to SynchroniserPart. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to TorqueConverterPump. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    @property
    def connected_component_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'ConnectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.ConnectedComponent.__class__.__mro__:
            raise CastException('Failed to cast connected_component to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.ConnectedComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectedComponent.__class__)(self.wrapped.ConnectedComponent) if self.wrapped.ConnectedComponent is not None else None

    def delete(self):
        ''' 'Delete' is the original name of this method.'''

        self.wrapped.Delete()

    def swap(self):
        ''' 'Swap' is the original name of this method.'''

        self.wrapped.Swap()
