'''_5483.py

PartHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model import (
    _2209, _2176, _2177, _2178,
    _2179, _2182, _2184, _2185,
    _2186, _2189, _2190, _2193,
    _2194, _2195, _2196, _2203,
    _2204, _2205, _2207, _2210,
    _2212, _2213, _2215, _2217,
    _2218, _2220
)
from mastapy._internal import constructor
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
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5465
from mastapy.system_model.analyses_and_results.modal_analyses import (
    _4905, _4820, _4821, _4822,
    _4825, _4826, _4827, _4828,
    _4830, _4832, _4833, _4834,
    _4835, _4837, _4838, _4839,
    _4840, _4842, _4843, _4845,
    _4847, _4848, _4850, _4851,
    _4853, _4854, _4856, _4859,
    _4860, _4862, _4863, _4864,
    _4866, _4869, _4870, _4871,
    _4872, _4873, _4875, _4876,
    _4877, _4878, _4881, _4882,
    _4883, _4885, _4886, _4889,
    _4890, _4892, _4893, _4895,
    _4896, _4897, _4898, _4902,
    _4903, _4907, _4908, _4910,
    _4911, _4912, _4913, _4914,
    _4915, _4917, _4919, _4920,
    _4921, _4922, _4925, _4927,
    _4928, _4930, _4931, _4933,
    _4934, _4936, _4937, _4938,
    _4939, _4940, _4941, _4942,
    _4943, _4945, _4946, _4947,
    _4948, _4949, _4956, _4957,
    _4959, _4960
)
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5746
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6790
from mastapy.system_model.analyses_and_results.analysis_cases import _7265
from mastapy._internal.python_net import python_net_import

_PART_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'PartHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('PartHarmonicAnalysisOfSingleExcitation',)


class PartHarmonicAnalysisOfSingleExcitation(_7265.PartStaticLoadAnalysisCase):
    '''PartHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _PART_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2209.Part':
        '''Part: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2209.Part.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Part. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_assembly(self) -> '_2176.Assembly':
        '''Assembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2176.Assembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Assembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_abstract_assembly(self) -> '_2177.AbstractAssembly':
        '''AbstractAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2177.AbstractAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Bearing. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.Bolt.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Bolt. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bolted_joint(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2185.BoltedJoint.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BoltedJoint. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_component(self) -> '_2186.Component':
        '''Component: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.Component.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Component. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Connector. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.Datum.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Datum. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2193.ExternalCADModel.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ExternalCADModel. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to FEPart. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_flexible_pin_assembly(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2195.FlexiblePinAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to FlexiblePinAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.GuideDxfModel.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to GuideDxfModel. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to MassDisc. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to MeasurementComponent. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to MountableComponent. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to OilSeal. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PlanetCarrier. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PointLoad. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PowerLoad. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_root_assembly(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2215.RootAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to RootAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_specialised_assembly(self) -> '_2217.SpecialisedAssembly':
        '''SpecialisedAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2217.SpecialisedAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SpecialisedAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to UnbalancedMass. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to VirtualComponent. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Shaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_agma_gleason_conical_gear_set(self) -> '_2254.AGMAGleasonConicalGearSet':
        '''AGMAGleasonConicalGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2254.AGMAGleasonConicalGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AGMAGleasonConicalGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_differential_gear_set(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2256.BevelDifferentialGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelDifferentialGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bevel_gear_set(self) -> '_2260.BevelGearSet':
        '''BevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2260.BevelGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConceptGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_concept_gear_set(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2262.ConceptGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConceptGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConicalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_conical_gear_set(self) -> '_2264.ConicalGearSet':
        '''ConicalGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2264.ConicalGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConicalGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cylindrical_gear_set(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to FaceGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_face_gear_set(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2269.FaceGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to FaceGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Gear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_gear_set(self) -> '_2272.GearSet':
        '''GearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2272.GearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to GearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to HypoidGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_hypoid_gear_set(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2275.HypoidGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to HypoidGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        '''KlingelnbergCycloPalloidConicalGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2277.KlingelnbergCycloPalloidConicalGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidConicalGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidHypoidGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to KlingelnbergCycloPalloidSpiralBevelGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_planetary_gear_set(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2282.PlanetaryGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PlanetaryGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SpiralBevelGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_spiral_bevel_gear_set(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2284.SpiralBevelGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SpiralBevelGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_diff_gear_set(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2286.StraightBevelDiffGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelDiffGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_gear_set(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2288.StraightBevelGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to WormGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_worm_gear_set(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2292.WormGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to WormGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ZerolBevelGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_zerol_bevel_gear_set(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2294.ZerolBevelGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ZerolBevelGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cycloidal_assembly(self) -> '_2308.CycloidalAssembly':
        '''CycloidalAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2308.CycloidalAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CycloidalAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CycloidalDisc. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to RingPins. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_belt_drive(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2316.BeltDrive.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BeltDrive. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_clutch(self) -> '_2318.Clutch':
        '''Clutch: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2318.Clutch.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Clutch. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ClutchHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_concept_coupling(self) -> '_2321.ConceptCoupling':
        '''ConceptCoupling: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2321.ConceptCoupling.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConceptCoupling. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_coupling(self) -> '_2323.Coupling':
        '''Coupling: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2323.Coupling.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Coupling. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CouplingHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cvt(self) -> '_2326.CVT':
        '''CVT: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2326.CVT.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CVT. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CVTPulley. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_part_to_part_shear_coupling(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2328.PartToPartShearCoupling.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PartToPartShearCoupling. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Pulley. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to RollingRing. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_rolling_ring_assembly(self) -> '_2337.RollingRingAssembly':
        '''RollingRingAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2337.RollingRingAssembly.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to RollingRingAssembly. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ShaftHubConnection. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_spring_damper(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2340.SpringDamper.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SpringDamper. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SpringDamperHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_synchroniser(self) -> '_2342.Synchroniser':
        '''Synchroniser: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2342.Synchroniser.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Synchroniser. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SynchroniserHalf. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SynchroniserPart. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_torque_converter(self) -> '_2347.TorqueConverter':
        '''TorqueConverter: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2347.TorqueConverter.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to TorqueConverter. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to TorqueConverterPump. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def harmonic_analysis_of_single_excitation(self) -> '_5465.HarmonicAnalysisOfSingleExcitation':
        '''HarmonicAnalysisOfSingleExcitation: 'HarmonicAnalysisOfSingleExcitation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5465.HarmonicAnalysisOfSingleExcitation)(self.wrapped.HarmonicAnalysisOfSingleExcitation) if self.wrapped.HarmonicAnalysisOfSingleExcitation is not None else None

    @property
    def uncoupled_modal_analysis(self) -> '_4905.PartModalAnalysis':
        '''PartModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4905.PartModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PartModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_abstract_assembly_modal_analysis(self) -> '_4820.AbstractAssemblyModalAnalysis':
        '''AbstractAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4820.AbstractAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AbstractAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_abstract_shaft_modal_analysis(self) -> '_4821.AbstractShaftModalAnalysis':
        '''AbstractShaftModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4821.AbstractShaftModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AbstractShaftModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_abstract_shaft_or_housing_modal_analysis(self) -> '_4822.AbstractShaftOrHousingModalAnalysis':
        '''AbstractShaftOrHousingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4822.AbstractShaftOrHousingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AbstractShaftOrHousingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_agma_gleason_conical_gear_modal_analysis(self) -> '_4825.AGMAGleasonConicalGearModalAnalysis':
        '''AGMAGleasonConicalGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4825.AGMAGleasonConicalGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AGMAGleasonConicalGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_agma_gleason_conical_gear_set_modal_analysis(self) -> '_4826.AGMAGleasonConicalGearSetModalAnalysis':
        '''AGMAGleasonConicalGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4826.AGMAGleasonConicalGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AGMAGleasonConicalGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_assembly_modal_analysis(self) -> '_4827.AssemblyModalAnalysis':
        '''AssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4827.AssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to AssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bearing_modal_analysis(self) -> '_4828.BearingModalAnalysis':
        '''BearingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4828.BearingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BearingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_belt_drive_modal_analysis(self) -> '_4830.BeltDriveModalAnalysis':
        '''BeltDriveModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4830.BeltDriveModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BeltDriveModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_differential_gear_modal_analysis(self) -> '_4832.BevelDifferentialGearModalAnalysis':
        '''BevelDifferentialGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4832.BevelDifferentialGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelDifferentialGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_differential_gear_set_modal_analysis(self) -> '_4833.BevelDifferentialGearSetModalAnalysis':
        '''BevelDifferentialGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4833.BevelDifferentialGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelDifferentialGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_differential_planet_gear_modal_analysis(self) -> '_4834.BevelDifferentialPlanetGearModalAnalysis':
        '''BevelDifferentialPlanetGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4834.BevelDifferentialPlanetGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelDifferentialPlanetGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_differential_sun_gear_modal_analysis(self) -> '_4835.BevelDifferentialSunGearModalAnalysis':
        '''BevelDifferentialSunGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4835.BevelDifferentialSunGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelDifferentialSunGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_gear_modal_analysis(self) -> '_4837.BevelGearModalAnalysis':
        '''BevelGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4837.BevelGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bevel_gear_set_modal_analysis(self) -> '_4838.BevelGearSetModalAnalysis':
        '''BevelGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4838.BevelGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BevelGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bolted_joint_modal_analysis(self) -> '_4839.BoltedJointModalAnalysis':
        '''BoltedJointModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4839.BoltedJointModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BoltedJointModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_bolt_modal_analysis(self) -> '_4840.BoltModalAnalysis':
        '''BoltModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4840.BoltModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to BoltModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_clutch_half_modal_analysis(self) -> '_4842.ClutchHalfModalAnalysis':
        '''ClutchHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4842.ClutchHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ClutchHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_clutch_modal_analysis(self) -> '_4843.ClutchModalAnalysis':
        '''ClutchModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4843.ClutchModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ClutchModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_component_modal_analysis(self) -> '_4845.ComponentModalAnalysis':
        '''ComponentModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4845.ComponentModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ComponentModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_concept_coupling_half_modal_analysis(self) -> '_4847.ConceptCouplingHalfModalAnalysis':
        '''ConceptCouplingHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4847.ConceptCouplingHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConceptCouplingHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_concept_coupling_modal_analysis(self) -> '_4848.ConceptCouplingModalAnalysis':
        '''ConceptCouplingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4848.ConceptCouplingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConceptCouplingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_concept_gear_modal_analysis(self) -> '_4850.ConceptGearModalAnalysis':
        '''ConceptGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4850.ConceptGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConceptGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_concept_gear_set_modal_analysis(self) -> '_4851.ConceptGearSetModalAnalysis':
        '''ConceptGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4851.ConceptGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConceptGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_conical_gear_modal_analysis(self) -> '_4853.ConicalGearModalAnalysis':
        '''ConicalGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4853.ConicalGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConicalGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_conical_gear_set_modal_analysis(self) -> '_4854.ConicalGearSetModalAnalysis':
        '''ConicalGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4854.ConicalGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConicalGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_connector_modal_analysis(self) -> '_4856.ConnectorModalAnalysis':
        '''ConnectorModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4856.ConnectorModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ConnectorModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_coupling_half_modal_analysis(self) -> '_4859.CouplingHalfModalAnalysis':
        '''CouplingHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4859.CouplingHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CouplingHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_coupling_modal_analysis(self) -> '_4860.CouplingModalAnalysis':
        '''CouplingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4860.CouplingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CouplingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cvt_modal_analysis(self) -> '_4862.CVTModalAnalysis':
        '''CVTModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4862.CVTModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CVTModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cvt_pulley_modal_analysis(self) -> '_4863.CVTPulleyModalAnalysis':
        '''CVTPulleyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4863.CVTPulleyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CVTPulleyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cycloidal_assembly_modal_analysis(self) -> '_4864.CycloidalAssemblyModalAnalysis':
        '''CycloidalAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4864.CycloidalAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CycloidalAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cycloidal_disc_modal_analysis(self) -> '_4866.CycloidalDiscModalAnalysis':
        '''CycloidalDiscModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4866.CycloidalDiscModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CycloidalDiscModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cylindrical_gear_modal_analysis(self) -> '_4869.CylindricalGearModalAnalysis':
        '''CylindricalGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4869.CylindricalGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CylindricalGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cylindrical_gear_set_modal_analysis(self) -> '_4870.CylindricalGearSetModalAnalysis':
        '''CylindricalGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4870.CylindricalGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CylindricalGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_cylindrical_planet_gear_modal_analysis(self) -> '_4871.CylindricalPlanetGearModalAnalysis':
        '''CylindricalPlanetGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4871.CylindricalPlanetGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to CylindricalPlanetGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_datum_modal_analysis(self) -> '_4872.DatumModalAnalysis':
        '''DatumModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4872.DatumModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to DatumModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_external_cad_model_modal_analysis(self) -> '_4873.ExternalCADModelModalAnalysis':
        '''ExternalCADModelModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4873.ExternalCADModelModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ExternalCADModelModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_face_gear_modal_analysis(self) -> '_4875.FaceGearModalAnalysis':
        '''FaceGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4875.FaceGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to FaceGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_face_gear_set_modal_analysis(self) -> '_4876.FaceGearSetModalAnalysis':
        '''FaceGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4876.FaceGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to FaceGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_fe_part_modal_analysis(self) -> '_4877.FEPartModalAnalysis':
        '''FEPartModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4877.FEPartModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to FEPartModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_flexible_pin_assembly_modal_analysis(self) -> '_4878.FlexiblePinAssemblyModalAnalysis':
        '''FlexiblePinAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4878.FlexiblePinAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to FlexiblePinAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_gear_modal_analysis(self) -> '_4881.GearModalAnalysis':
        '''GearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4881.GearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to GearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_gear_set_modal_analysis(self) -> '_4882.GearSetModalAnalysis':
        '''GearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4882.GearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to GearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_guide_dxf_model_modal_analysis(self) -> '_4883.GuideDxfModelModalAnalysis':
        '''GuideDxfModelModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4883.GuideDxfModelModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to GuideDxfModelModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_hypoid_gear_modal_analysis(self) -> '_4885.HypoidGearModalAnalysis':
        '''HypoidGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4885.HypoidGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to HypoidGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_hypoid_gear_set_modal_analysis(self) -> '_4886.HypoidGearSetModalAnalysis':
        '''HypoidGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4886.HypoidGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to HypoidGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_conical_gear_modal_analysis(self) -> '_4889.KlingelnbergCycloPalloidConicalGearModalAnalysis':
        '''KlingelnbergCycloPalloidConicalGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4889.KlingelnbergCycloPalloidConicalGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidConicalGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_conical_gear_set_modal_analysis(self) -> '_4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis':
        '''KlingelnbergCycloPalloidConicalGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidConicalGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis(self) -> '_4892.KlingelnbergCycloPalloidHypoidGearModalAnalysis':
        '''KlingelnbergCycloPalloidHypoidGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4892.KlingelnbergCycloPalloidHypoidGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidHypoidGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_modal_analysis(self) -> '_4893.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis':
        '''KlingelnbergCycloPalloidHypoidGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4893.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidHypoidGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis(self) -> '_4895.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis':
        '''KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4895.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_modal_analysis(self) -> '_4896.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4896.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_mass_disc_modal_analysis(self) -> '_4897.MassDiscModalAnalysis':
        '''MassDiscModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4897.MassDiscModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to MassDiscModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_measurement_component_modal_analysis(self) -> '_4898.MeasurementComponentModalAnalysis':
        '''MeasurementComponentModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4898.MeasurementComponentModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to MeasurementComponentModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_mountable_component_modal_analysis(self) -> '_4902.MountableComponentModalAnalysis':
        '''MountableComponentModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4902.MountableComponentModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to MountableComponentModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_oil_seal_modal_analysis(self) -> '_4903.OilSealModalAnalysis':
        '''OilSealModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4903.OilSealModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to OilSealModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_part_to_part_shear_coupling_half_modal_analysis(self) -> '_4907.PartToPartShearCouplingHalfModalAnalysis':
        '''PartToPartShearCouplingHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4907.PartToPartShearCouplingHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PartToPartShearCouplingHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_part_to_part_shear_coupling_modal_analysis(self) -> '_4908.PartToPartShearCouplingModalAnalysis':
        '''PartToPartShearCouplingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4908.PartToPartShearCouplingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PartToPartShearCouplingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_planetary_gear_set_modal_analysis(self) -> '_4910.PlanetaryGearSetModalAnalysis':
        '''PlanetaryGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4910.PlanetaryGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PlanetaryGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_planet_carrier_modal_analysis(self) -> '_4911.PlanetCarrierModalAnalysis':
        '''PlanetCarrierModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4911.PlanetCarrierModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PlanetCarrierModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_point_load_modal_analysis(self) -> '_4912.PointLoadModalAnalysis':
        '''PointLoadModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4912.PointLoadModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PointLoadModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_power_load_modal_analysis(self) -> '_4913.PowerLoadModalAnalysis':
        '''PowerLoadModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4913.PowerLoadModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PowerLoadModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_pulley_modal_analysis(self) -> '_4914.PulleyModalAnalysis':
        '''PulleyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4914.PulleyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to PulleyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_ring_pins_modal_analysis(self) -> '_4915.RingPinsModalAnalysis':
        '''RingPinsModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4915.RingPinsModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to RingPinsModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_rolling_ring_assembly_modal_analysis(self) -> '_4917.RollingRingAssemblyModalAnalysis':
        '''RollingRingAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4917.RollingRingAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to RollingRingAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_rolling_ring_modal_analysis(self) -> '_4919.RollingRingModalAnalysis':
        '''RollingRingModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4919.RollingRingModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to RollingRingModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_root_assembly_modal_analysis(self) -> '_4920.RootAssemblyModalAnalysis':
        '''RootAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4920.RootAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to RootAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_shaft_hub_connection_modal_analysis(self) -> '_4921.ShaftHubConnectionModalAnalysis':
        '''ShaftHubConnectionModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4921.ShaftHubConnectionModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ShaftHubConnectionModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_shaft_modal_analysis(self) -> '_4922.ShaftModalAnalysis':
        '''ShaftModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4922.ShaftModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ShaftModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_specialised_assembly_modal_analysis(self) -> '_4925.SpecialisedAssemblyModalAnalysis':
        '''SpecialisedAssemblyModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4925.SpecialisedAssemblyModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SpecialisedAssemblyModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_spiral_bevel_gear_modal_analysis(self) -> '_4927.SpiralBevelGearModalAnalysis':
        '''SpiralBevelGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4927.SpiralBevelGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SpiralBevelGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_spiral_bevel_gear_set_modal_analysis(self) -> '_4928.SpiralBevelGearSetModalAnalysis':
        '''SpiralBevelGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4928.SpiralBevelGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SpiralBevelGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_spring_damper_half_modal_analysis(self) -> '_4930.SpringDamperHalfModalAnalysis':
        '''SpringDamperHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4930.SpringDamperHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SpringDamperHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_spring_damper_modal_analysis(self) -> '_4931.SpringDamperModalAnalysis':
        '''SpringDamperModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4931.SpringDamperModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SpringDamperModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_diff_gear_modal_analysis(self) -> '_4933.StraightBevelDiffGearModalAnalysis':
        '''StraightBevelDiffGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4933.StraightBevelDiffGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelDiffGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_diff_gear_set_modal_analysis(self) -> '_4934.StraightBevelDiffGearSetModalAnalysis':
        '''StraightBevelDiffGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4934.StraightBevelDiffGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelDiffGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_gear_modal_analysis(self) -> '_4936.StraightBevelGearModalAnalysis':
        '''StraightBevelGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4936.StraightBevelGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_gear_set_modal_analysis(self) -> '_4937.StraightBevelGearSetModalAnalysis':
        '''StraightBevelGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4937.StraightBevelGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_planet_gear_modal_analysis(self) -> '_4938.StraightBevelPlanetGearModalAnalysis':
        '''StraightBevelPlanetGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4938.StraightBevelPlanetGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelPlanetGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_straight_bevel_sun_gear_modal_analysis(self) -> '_4939.StraightBevelSunGearModalAnalysis':
        '''StraightBevelSunGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4939.StraightBevelSunGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to StraightBevelSunGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_synchroniser_half_modal_analysis(self) -> '_4940.SynchroniserHalfModalAnalysis':
        '''SynchroniserHalfModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4940.SynchroniserHalfModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SynchroniserHalfModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_synchroniser_modal_analysis(self) -> '_4941.SynchroniserModalAnalysis':
        '''SynchroniserModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4941.SynchroniserModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SynchroniserModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_synchroniser_part_modal_analysis(self) -> '_4942.SynchroniserPartModalAnalysis':
        '''SynchroniserPartModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4942.SynchroniserPartModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SynchroniserPartModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_synchroniser_sleeve_modal_analysis(self) -> '_4943.SynchroniserSleeveModalAnalysis':
        '''SynchroniserSleeveModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4943.SynchroniserSleeveModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to SynchroniserSleeveModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_torque_converter_modal_analysis(self) -> '_4945.TorqueConverterModalAnalysis':
        '''TorqueConverterModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4945.TorqueConverterModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to TorqueConverterModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_torque_converter_pump_modal_analysis(self) -> '_4946.TorqueConverterPumpModalAnalysis':
        '''TorqueConverterPumpModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4946.TorqueConverterPumpModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to TorqueConverterPumpModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_torque_converter_turbine_modal_analysis(self) -> '_4947.TorqueConverterTurbineModalAnalysis':
        '''TorqueConverterTurbineModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4947.TorqueConverterTurbineModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to TorqueConverterTurbineModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_unbalanced_mass_modal_analysis(self) -> '_4948.UnbalancedMassModalAnalysis':
        '''UnbalancedMassModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4948.UnbalancedMassModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to UnbalancedMassModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_virtual_component_modal_analysis(self) -> '_4949.VirtualComponentModalAnalysis':
        '''VirtualComponentModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4949.VirtualComponentModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to VirtualComponentModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_worm_gear_modal_analysis(self) -> '_4956.WormGearModalAnalysis':
        '''WormGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4956.WormGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to WormGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_worm_gear_set_modal_analysis(self) -> '_4957.WormGearSetModalAnalysis':
        '''WormGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4957.WormGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to WormGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_zerol_bevel_gear_modal_analysis(self) -> '_4959.ZerolBevelGearModalAnalysis':
        '''ZerolBevelGearModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4959.ZerolBevelGearModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ZerolBevelGearModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def uncoupled_modal_analysis_of_type_zerol_bevel_gear_set_modal_analysis(self) -> '_4960.ZerolBevelGearSetModalAnalysis':
        '''ZerolBevelGearSetModalAnalysis: 'UncoupledModalAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4960.ZerolBevelGearSetModalAnalysis.TYPE not in self.wrapped.UncoupledModalAnalysis.__class__.__mro__:
            raise CastException('Failed to cast uncoupled_modal_analysis to ZerolBevelGearSetModalAnalysis. Expected: {}.'.format(self.wrapped.UncoupledModalAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.UncoupledModalAnalysis.__class__)(self.wrapped.UncoupledModalAnalysis) if self.wrapped.UncoupledModalAnalysis is not None else None

    @property
    def harmonic_analysis_options(self) -> '_5746.HarmonicAnalysisOptions':
        '''HarmonicAnalysisOptions: 'HarmonicAnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5746.HarmonicAnalysisOptions.TYPE not in self.wrapped.HarmonicAnalysisOptions.__class__.__mro__:
            raise CastException('Failed to cast harmonic_analysis_options to HarmonicAnalysisOptions. Expected: {}.'.format(self.wrapped.HarmonicAnalysisOptions.__class__.__qualname__))

        return constructor.new_override(self.wrapped.HarmonicAnalysisOptions.__class__)(self.wrapped.HarmonicAnalysisOptions) if self.wrapped.HarmonicAnalysisOptions is not None else None
