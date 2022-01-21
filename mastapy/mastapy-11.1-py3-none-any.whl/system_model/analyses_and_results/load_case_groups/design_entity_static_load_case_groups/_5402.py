'''_5402.py

PartStaticLoadCaseGroup
'''


from typing import List

from mastapy.system_model.part_model import (
    _2209, _2176, _2177, _2178,
    _2179, _2182, _2184, _2185,
    _2186, _2189, _2190, _2193,
    _2194, _2195, _2196, _2203,
    _2204, _2205, _2207, _2210,
    _2212, _2213, _2215, _2217,
    _2218, _2220
)
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.gears import (
    _2253, _2254, _2255, _2256,
    _2257, _2258, _2259, _2260,
    _2261, _2262, _2263, _2264,
    _2265, _2266, _2267, _2268,
    _2269, _2270, _2272, _2274,
    _2275, _2276, _2277, _2278,
    _2279, _2280, _2281, _2282,
    _2283, _2284, _2285, _2286,
    _2287, _2288, _2289, _2290,
    _2291, _2292, _2293, _2294
)
from mastapy.system_model.part_model.cycloidal import _2308, _2309, _2310
from mastapy.system_model.part_model.couplings import (
    _2316, _2318, _2319, _2321,
    _2322, _2323, _2324, _2326,
    _2327, _2328, _2329, _2330,
    _2336, _2337, _2338, _2340,
    _2341, _2342, _2344, _2345,
    _2346, _2347, _2348, _2350
)
from mastapy.system_model.analyses_and_results.static_loads import _6646
from mastapy.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups import _5400
from mastapy._internal.python_net import python_net_import

_PART_STATIC_LOAD_CASE_GROUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups.DesignEntityStaticLoadCaseGroups', 'PartStaticLoadCaseGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('PartStaticLoadCaseGroup',)


class PartStaticLoadCaseGroup(_5400.DesignEntityStaticLoadCaseGroup):
    '''PartStaticLoadCaseGroup

    This is a mastapy class.
    '''

    TYPE = _PART_STATIC_LOAD_CASE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartStaticLoadCaseGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def part(self) -> '_2209.Part':
        '''Part: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2209.Part.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Part. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_assembly(self) -> '_2176.Assembly':
        '''Assembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2176.Assembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Assembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_abstract_assembly(self) -> '_2177.AbstractAssembly':
        '''AbstractAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2177.AbstractAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to AbstractAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to AbstractShaft. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Bearing. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.Bolt.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Bolt. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bolted_joint(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2185.BoltedJoint.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BoltedJoint. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_component(self) -> '_2186.Component':
        '''Component: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.Component.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Component. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Connector. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.Datum.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Datum. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2193.ExternalCADModel.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ExternalCADModel. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to FEPart. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_flexible_pin_assembly(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2195.FlexiblePinAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to FlexiblePinAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.GuideDxfModel.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to GuideDxfModel. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to MassDisc. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to MeasurementComponent. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to MountableComponent. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to OilSeal. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PlanetCarrier. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PointLoad. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PowerLoad. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_root_assembly(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2215.RootAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to RootAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_specialised_assembly(self) -> '_2217.SpecialisedAssembly':
        '''SpecialisedAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2217.SpecialisedAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SpecialisedAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to UnbalancedMass. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to VirtualComponent. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Shaft. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_agma_gleason_conical_gear_set(self) -> '_2254.AGMAGleasonConicalGearSet':
        '''AGMAGleasonConicalGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2254.AGMAGleasonConicalGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to AGMAGleasonConicalGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_differential_gear_set(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2256.BevelDifferentialGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelDifferentialGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_bevel_gear_set(self) -> '_2260.BevelGearSet':
        '''BevelGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2260.BevelGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BevelGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConceptGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_concept_gear_set(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2262.ConceptGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConceptGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConicalGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_conical_gear_set(self) -> '_2264.ConicalGearSet':
        '''ConicalGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2264.ConicalGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConicalGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CylindricalGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cylindrical_gear_set(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CylindricalGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to FaceGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_face_gear_set(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2269.FaceGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to FaceGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Gear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_gear_set(self) -> '_2272.GearSet':
        '''GearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2272.GearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to GearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to HypoidGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_hypoid_gear_set(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2275.HypoidGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to HypoidGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        '''KlingelnbergCycloPalloidConicalGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2277.KlingelnbergCycloPalloidConicalGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidConicalGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidHypoidGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to KlingelnbergCycloPalloidSpiralBevelGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_planetary_gear_set(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2282.PlanetaryGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PlanetaryGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SpiralBevelGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_spiral_bevel_gear_set(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2284.SpiralBevelGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SpiralBevelGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_diff_gear_set(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2286.StraightBevelDiffGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelDiffGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_gear_set(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2288.StraightBevelGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to WormGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_worm_gear_set(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2292.WormGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to WormGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ZerolBevelGear. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_zerol_bevel_gear_set(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2294.ZerolBevelGearSet.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ZerolBevelGearSet. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cycloidal_assembly(self) -> '_2308.CycloidalAssembly':
        '''CycloidalAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2308.CycloidalAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CycloidalAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CycloidalDisc. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to RingPins. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_belt_drive(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2316.BeltDrive.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to BeltDrive. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_clutch(self) -> '_2318.Clutch':
        '''Clutch: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2318.Clutch.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Clutch. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ClutchHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_concept_coupling(self) -> '_2321.ConceptCoupling':
        '''ConceptCoupling: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2321.ConceptCoupling.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConceptCoupling. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_coupling(self) -> '_2323.Coupling':
        '''Coupling: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2323.Coupling.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Coupling. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CouplingHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cvt(self) -> '_2326.CVT':
        '''CVT: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2326.CVT.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CVT. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to CVTPulley. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_part_to_part_shear_coupling(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2328.PartToPartShearCoupling.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PartToPartShearCoupling. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Pulley. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to RollingRing. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_rolling_ring_assembly(self) -> '_2337.RollingRingAssembly':
        '''RollingRingAssembly: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2337.RollingRingAssembly.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to RollingRingAssembly. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to ShaftHubConnection. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_spring_damper(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2340.SpringDamper.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SpringDamper. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SpringDamperHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_synchroniser(self) -> '_2342.Synchroniser':
        '''Synchroniser: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2342.Synchroniser.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to Synchroniser. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SynchroniserHalf. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SynchroniserPart. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_torque_converter(self) -> '_2347.TorqueConverter':
        '''TorqueConverter: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2347.TorqueConverter.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to TorqueConverter. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to TorqueConverterPump. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'Part' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.Part.__class__.__mro__:
            raise CastException('Failed to cast part to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.Part.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Part.__class__)(self.wrapped.Part) if self.wrapped.Part is not None else None

    @property
    def part_load_cases(self) -> 'List[_6646.PartLoadCase]':
        '''List[PartLoadCase]: 'PartLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PartLoadCases, constructor.new(_6646.PartLoadCase))
        return value

    def clear_user_specified_excitation_data_for_all_load_cases(self):
        ''' 'ClearUserSpecifiedExcitationDataForAllLoadCases' is the original name of this method.'''

        self.wrapped.ClearUserSpecifiedExcitationDataForAllLoadCases()
