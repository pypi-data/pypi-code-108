'''_2415.py

CompoundMultibodyDynamicsAnalysis
'''


from typing import Iterable

from mastapy.system_model.connections_and_sockets.couplings import (
    _2092, _2094, _2090, _2084,
    _2086, _2088
)
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import (
    _5357, _5372, _5255, _5254,
    _5256, _5262, _5273, _5274,
    _5279, _5290, _5305, _5306,
    _5310, _5311, _5261, _5315,
    _5329, _5330, _5331, _5332,
    _5333, _5339, _5340, _5341,
    _5348, _5352, _5375, _5376,
    _5349, _5283, _5285, _5307,
    _5309, _5258, _5260, _5265,
    _5267, _5268, _5269, _5270,
    _5272, _5286, _5288, _5301,
    _5303, _5304, _5312, _5314,
    _5316, _5318, _5320, _5322,
    _5323, _5325, _5326, _5328,
    _5338, _5353, _5355, _5359,
    _5361, _5362, _5364, _5365,
    _5366, _5377, _5379, _5380,
    _5382, _5297, _5299, _5343,
    _5334, _5336, _5264, _5275,
    _5277, _5280, _5282, _5291,
    _5293, _5295, _5296, _5342,
    _5350, _5346, _5345, _5356,
    _5358, _5367, _5368, _5369,
    _5370, _5371, _5373, _5374,
    _5351, _5294, _5263, _5278,
    _5289, _5319, _5337, _5347,
    _5257, _5266, _5284, _5308,
    _5360, _5271, _5287, _5259,
    _5302, _5317, _5321, _5324,
    _5327, _5354, _5363, _5378,
    _5381, _5313, _5298, _5300,
    _5344, _5335, _5276, _5281,
    _5292
)
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import (
    _2178, _2177, _2179, _2182,
    _2184, _2185, _2186, _2189,
    _2190, _2193, _2194, _2195,
    _2176, _2196, _2203, _2204,
    _2205, _2207, _2209, _2210,
    _2212, _2213, _2215, _2217,
    _2218, _2220
)
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.gears import (
    _2261, _2262, _2268, _2269,
    _2253, _2254, _2255, _2256,
    _2257, _2258, _2259, _2260,
    _2263, _2264, _2265, _2266,
    _2267, _2270, _2272, _2274,
    _2275, _2276, _2277, _2278,
    _2279, _2280, _2281, _2282,
    _2283, _2284, _2285, _2286,
    _2287, _2288, _2289, _2290,
    _2291, _2292, _2293, _2294
)
from mastapy.system_model.part_model.cycloidal import _2308, _2309, _2310
from mastapy.system_model.part_model.couplings import (
    _2328, _2329, _2316, _2318,
    _2319, _2321, _2322, _2323,
    _2324, _2326, _2327, _2330,
    _2338, _2336, _2337, _2340,
    _2341, _2342, _2344, _2345,
    _2346, _2347, _2348, _2350
)
from mastapy.system_model.connections_and_sockets import (
    _2037, _2015, _2010, _2011,
    _2014, _2023, _2029, _2034,
    _2007
)
from mastapy.system_model.connections_and_sockets.gears import (
    _2043, _2047, _2053, _2067,
    _2045, _2049, _2041, _2051,
    _2057, _2060, _2061, _2062,
    _2065, _2069, _2071, _2073,
    _2055
)
from mastapy.system_model.connections_and_sockets.cycloidal import _2077, _2080, _2083
from mastapy._internal.python_net import python_net_import
from mastapy.system_model.analyses_and_results import _2359

_SPRING_DAMPER_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'SpringDamperConnection')
_TORQUE_CONVERTER_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'TorqueConverterConnection')
_PART_TO_PART_SHEAR_COUPLING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'PartToPartShearCouplingConnection')
_CLUTCH_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'ClutchConnection')
_CONCEPT_COUPLING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'ConceptCouplingConnection')
_COUPLING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'CouplingConnection')
_ABSTRACT_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractShaft')
_ABSTRACT_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractAssembly')
_ABSTRACT_SHAFT_OR_HOUSING = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractShaftOrHousing')
_BEARING = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Bearing')
_BOLT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Bolt')
_BOLTED_JOINT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'BoltedJoint')
_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Component')
_CONNECTOR = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Connector')
_DATUM = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Datum')
_EXTERNAL_CAD_MODEL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'ExternalCADModel')
_FE_PART = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'FEPart')
_FLEXIBLE_PIN_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'FlexiblePinAssembly')
_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Assembly')
_GUIDE_DXF_MODEL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'GuideDxfModel')
_MASS_DISC = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'MassDisc')
_MEASUREMENT_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'MeasurementComponent')
_MOUNTABLE_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'MountableComponent')
_OIL_SEAL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'OilSeal')
_PART = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Part')
_PLANET_CARRIER = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'PlanetCarrier')
_POINT_LOAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'PointLoad')
_POWER_LOAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'PowerLoad')
_ROOT_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'RootAssembly')
_SPECIALISED_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'SpecialisedAssembly')
_UNBALANCED_MASS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'UnbalancedMass')
_VIRTUAL_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'VirtualComponent')
_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ShaftModel', 'Shaft')
_CONCEPT_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ConceptGear')
_CONCEPT_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ConceptGearSet')
_FACE_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'FaceGear')
_FACE_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'FaceGearSet')
_AGMA_GLEASON_CONICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'AGMAGleasonConicalGear')
_AGMA_GLEASON_CONICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'AGMAGleasonConicalGearSet')
_BEVEL_DIFFERENTIAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialGear')
_BEVEL_DIFFERENTIAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialGearSet')
_BEVEL_DIFFERENTIAL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialPlanetGear')
_BEVEL_DIFFERENTIAL_SUN_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialSunGear')
_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelGear')
_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelGearSet')
_CONICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ConicalGear')
_CONICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ConicalGearSet')
_CYLINDRICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalGear')
_CYLINDRICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalGearSet')
_CYLINDRICAL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalPlanetGear')
_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'Gear')
_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'GearSet')
_HYPOID_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'HypoidGear')
_HYPOID_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'HypoidGearSet')
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidConicalGear')
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidConicalGearSet')
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidHypoidGear')
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidHypoidGearSet')
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidSpiralBevelGear')
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidSpiralBevelGearSet')
_PLANETARY_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'PlanetaryGearSet')
_SPIRAL_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'SpiralBevelGear')
_SPIRAL_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'SpiralBevelGearSet')
_STRAIGHT_BEVEL_DIFF_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelDiffGear')
_STRAIGHT_BEVEL_DIFF_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelDiffGearSet')
_STRAIGHT_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelGear')
_STRAIGHT_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelGearSet')
_STRAIGHT_BEVEL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelPlanetGear')
_STRAIGHT_BEVEL_SUN_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelSunGear')
_WORM_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'WormGear')
_WORM_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'WormGearSet')
_ZEROL_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ZerolBevelGear')
_ZEROL_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ZerolBevelGearSet')
_CYCLOIDAL_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Cycloidal', 'CycloidalAssembly')
_CYCLOIDAL_DISC = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Cycloidal', 'CycloidalDisc')
_RING_PINS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Cycloidal', 'RingPins')
_PART_TO_PART_SHEAR_COUPLING = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'PartToPartShearCoupling')
_PART_TO_PART_SHEAR_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'PartToPartShearCouplingHalf')
_BELT_DRIVE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'BeltDrive')
_CLUTCH = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'Clutch')
_CLUTCH_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ClutchHalf')
_CONCEPT_COUPLING = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ConceptCoupling')
_CONCEPT_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ConceptCouplingHalf')
_COUPLING = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'Coupling')
_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CouplingHalf')
_CVT = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CVT')
_CVT_PULLEY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CVTPulley')
_PULLEY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'Pulley')
_SHAFT_HUB_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ShaftHubConnection')
_ROLLING_RING = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'RollingRing')
_ROLLING_RING_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'RollingRingAssembly')
_SPRING_DAMPER = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SpringDamper')
_SPRING_DAMPER_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SpringDamperHalf')
_SYNCHRONISER = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'Synchroniser')
_SYNCHRONISER_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SynchroniserHalf')
_SYNCHRONISER_PART = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SynchroniserPart')
_SYNCHRONISER_SLEEVE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SynchroniserSleeve')
_TORQUE_CONVERTER = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'TorqueConverter')
_TORQUE_CONVERTER_PUMP = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'TorqueConverterPump')
_TORQUE_CONVERTER_TURBINE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'TorqueConverterTurbine')
_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'ShaftToMountableComponentConnection')
_CVT_BELT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'CVTBeltConnection')
_BELT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'BeltConnection')
_COAXIAL_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'CoaxialConnection')
_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'Connection')
_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'InterMountableComponentConnection')
_PLANETARY_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'PlanetaryConnection')
_ROLLING_RING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'RollingRingConnection')
_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'AbstractShaftToMountableComponentConnection')
_BEVEL_DIFFERENTIAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'BevelDifferentialGearMesh')
_CONCEPT_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'ConceptGearMesh')
_FACE_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'FaceGearMesh')
_STRAIGHT_BEVEL_DIFF_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'StraightBevelDiffGearMesh')
_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'BevelGearMesh')
_CONICAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'ConicalGearMesh')
_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'AGMAGleasonConicalGearMesh')
_CYLINDRICAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'CylindricalGearMesh')
_HYPOID_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'HypoidGearMesh')
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergCycloPalloidConicalGearMesh')
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergCycloPalloidHypoidGearMesh')
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergCycloPalloidSpiralBevelGearMesh')
_SPIRAL_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'SpiralBevelGearMesh')
_STRAIGHT_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'StraightBevelGearMesh')
_WORM_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'WormGearMesh')
_ZEROL_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'ZerolBevelGearMesh')
_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'GearMesh')
_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscCentralBearingConnection')
_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'CycloidalDiscPlanetaryBearingConnection')
_RING_PINS_TO_DISC_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal', 'RingPinsToDiscConnection')
_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundMultibodyDynamicsAnalysis',)


class CompoundMultibodyDynamicsAnalysis(_2359.CompoundAnalysis):
    '''CompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def results_for_spring_damper_connection(self, design_entity: '_2092.SpringDamperConnection') -> 'Iterable[_5357.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.SpringDamperConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPRING_DAMPER_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5357.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_torque_converter_connection(self, design_entity: '_2094.TorqueConverterConnection') -> 'Iterable[_5372.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.TorqueConverterConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_TORQUE_CONVERTER_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5372.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_abstract_shaft(self, design_entity: '_2178.AbstractShaft') -> 'Iterable[_5255.AbstractShaftCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaft)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AbstractShaftCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ABSTRACT_SHAFT](design_entity.wrapped if design_entity else None), constructor.new(_5255.AbstractShaftCompoundMultibodyDynamicsAnalysis))

    def results_for_abstract_assembly(self, design_entity: '_2177.AbstractAssembly') -> 'Iterable[_5254.AbstractAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.AbstractAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AbstractAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ABSTRACT_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5254.AbstractAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_abstract_shaft_or_housing(self, design_entity: '_2179.AbstractShaftOrHousing') -> 'Iterable[_5256.AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaftOrHousing)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ABSTRACT_SHAFT_OR_HOUSING](design_entity.wrapped if design_entity else None), constructor.new(_5256.AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis))

    def results_for_bearing(self, design_entity: '_2182.Bearing') -> 'Iterable[_5262.BearingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Bearing)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BearingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEARING](design_entity.wrapped if design_entity else None), constructor.new(_5262.BearingCompoundMultibodyDynamicsAnalysis))

    def results_for_bolt(self, design_entity: '_2184.Bolt') -> 'Iterable[_5273.BoltCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Bolt)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BoltCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BOLT](design_entity.wrapped if design_entity else None), constructor.new(_5273.BoltCompoundMultibodyDynamicsAnalysis))

    def results_for_bolted_joint(self, design_entity: '_2185.BoltedJoint') -> 'Iterable[_5274.BoltedJointCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.BoltedJoint)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BoltedJointCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BOLTED_JOINT](design_entity.wrapped if design_entity else None), constructor.new(_5274.BoltedJointCompoundMultibodyDynamicsAnalysis))

    def results_for_component(self, design_entity: '_2186.Component') -> 'Iterable[_5279.ComponentCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Component)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ComponentCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_COMPONENT](design_entity.wrapped if design_entity else None), constructor.new(_5279.ComponentCompoundMultibodyDynamicsAnalysis))

    def results_for_connector(self, design_entity: '_2189.Connector') -> 'Iterable[_5290.ConnectorCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Connector)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConnectorCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONNECTOR](design_entity.wrapped if design_entity else None), constructor.new(_5290.ConnectorCompoundMultibodyDynamicsAnalysis))

    def results_for_datum(self, design_entity: '_2190.Datum') -> 'Iterable[_5305.DatumCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Datum)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.DatumCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_DATUM](design_entity.wrapped if design_entity else None), constructor.new(_5305.DatumCompoundMultibodyDynamicsAnalysis))

    def results_for_external_cad_model(self, design_entity: '_2193.ExternalCADModel') -> 'Iterable[_5306.ExternalCADModelCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.ExternalCADModel)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ExternalCADModelCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_EXTERNAL_CAD_MODEL](design_entity.wrapped if design_entity else None), constructor.new(_5306.ExternalCADModelCompoundMultibodyDynamicsAnalysis))

    def results_for_fe_part(self, design_entity: '_2194.FEPart') -> 'Iterable[_5310.FEPartCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.FEPart)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.FEPartCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_FE_PART](design_entity.wrapped if design_entity else None), constructor.new(_5310.FEPartCompoundMultibodyDynamicsAnalysis))

    def results_for_flexible_pin_assembly(self, design_entity: '_2195.FlexiblePinAssembly') -> 'Iterable[_5311.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.FlexiblePinAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_FLEXIBLE_PIN_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5311.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_assembly(self, design_entity: '_2176.Assembly') -> 'Iterable[_5261.AssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Assembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5261.AssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_guide_dxf_model(self, design_entity: '_2196.GuideDxfModel') -> 'Iterable[_5315.GuideDxfModelCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.GuideDxfModel)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.GuideDxfModelCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_GUIDE_DXF_MODEL](design_entity.wrapped if design_entity else None), constructor.new(_5315.GuideDxfModelCompoundMultibodyDynamicsAnalysis))

    def results_for_mass_disc(self, design_entity: '_2203.MassDisc') -> 'Iterable[_5329.MassDiscCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.MassDisc)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.MassDiscCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_MASS_DISC](design_entity.wrapped if design_entity else None), constructor.new(_5329.MassDiscCompoundMultibodyDynamicsAnalysis))

    def results_for_measurement_component(self, design_entity: '_2204.MeasurementComponent') -> 'Iterable[_5330.MeasurementComponentCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.MeasurementComponent)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.MeasurementComponentCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_MEASUREMENT_COMPONENT](design_entity.wrapped if design_entity else None), constructor.new(_5330.MeasurementComponentCompoundMultibodyDynamicsAnalysis))

    def results_for_mountable_component(self, design_entity: '_2205.MountableComponent') -> 'Iterable[_5331.MountableComponentCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.MountableComponent)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.MountableComponentCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_MOUNTABLE_COMPONENT](design_entity.wrapped if design_entity else None), constructor.new(_5331.MountableComponentCompoundMultibodyDynamicsAnalysis))

    def results_for_oil_seal(self, design_entity: '_2207.OilSeal') -> 'Iterable[_5332.OilSealCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.OilSeal)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.OilSealCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_OIL_SEAL](design_entity.wrapped if design_entity else None), constructor.new(_5332.OilSealCompoundMultibodyDynamicsAnalysis))

    def results_for_part(self, design_entity: '_2209.Part') -> 'Iterable[_5333.PartCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.Part)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PartCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PART](design_entity.wrapped if design_entity else None), constructor.new(_5333.PartCompoundMultibodyDynamicsAnalysis))

    def results_for_planet_carrier(self, design_entity: '_2210.PlanetCarrier') -> 'Iterable[_5339.PlanetCarrierCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.PlanetCarrier)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PlanetCarrierCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PLANET_CARRIER](design_entity.wrapped if design_entity else None), constructor.new(_5339.PlanetCarrierCompoundMultibodyDynamicsAnalysis))

    def results_for_point_load(self, design_entity: '_2212.PointLoad') -> 'Iterable[_5340.PointLoadCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.PointLoad)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PointLoadCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_POINT_LOAD](design_entity.wrapped if design_entity else None), constructor.new(_5340.PointLoadCompoundMultibodyDynamicsAnalysis))

    def results_for_power_load(self, design_entity: '_2213.PowerLoad') -> 'Iterable[_5341.PowerLoadCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.PowerLoad)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PowerLoadCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_POWER_LOAD](design_entity.wrapped if design_entity else None), constructor.new(_5341.PowerLoadCompoundMultibodyDynamicsAnalysis))

    def results_for_root_assembly(self, design_entity: '_2215.RootAssembly') -> 'Iterable[_5348.RootAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.RootAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RootAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ROOT_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5348.RootAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_specialised_assembly(self, design_entity: '_2217.SpecialisedAssembly') -> 'Iterable[_5352.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.SpecialisedAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPECIALISED_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5352.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_unbalanced_mass(self, design_entity: '_2218.UnbalancedMass') -> 'Iterable[_5375.UnbalancedMassCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.UnbalancedMass)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.UnbalancedMassCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_UNBALANCED_MASS](design_entity.wrapped if design_entity else None), constructor.new(_5375.UnbalancedMassCompoundMultibodyDynamicsAnalysis))

    def results_for_virtual_component(self, design_entity: '_2220.VirtualComponent') -> 'Iterable[_5376.VirtualComponentCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.VirtualComponent)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.VirtualComponentCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_VIRTUAL_COMPONENT](design_entity.wrapped if design_entity else None), constructor.new(_5376.VirtualComponentCompoundMultibodyDynamicsAnalysis))

    def results_for_shaft(self, design_entity: '_2223.Shaft') -> 'Iterable[_5349.ShaftCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.shaft_model.Shaft)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ShaftCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SHAFT](design_entity.wrapped if design_entity else None), constructor.new(_5349.ShaftCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_gear(self, design_entity: '_2261.ConceptGear') -> 'Iterable[_5283.ConceptGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5283.ConceptGearCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_gear_set(self, design_entity: '_2262.ConceptGearSet') -> 'Iterable[_5285.ConceptGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5285.ConceptGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_face_gear(self, design_entity: '_2268.FaceGear') -> 'Iterable[_5307.FaceGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.FaceGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_FACE_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5307.FaceGearCompoundMultibodyDynamicsAnalysis))

    def results_for_face_gear_set(self, design_entity: '_2269.FaceGearSet') -> 'Iterable[_5309.FaceGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.FaceGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_FACE_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5309.FaceGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_agma_gleason_conical_gear(self, design_entity: '_2253.AGMAGleasonConicalGear') -> 'Iterable[_5258.AGMAGleasonConicalGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AGMAGleasonConicalGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_AGMA_GLEASON_CONICAL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5258.AGMAGleasonConicalGearCompoundMultibodyDynamicsAnalysis))

    def results_for_agma_gleason_conical_gear_set(self, design_entity: '_2254.AGMAGleasonConicalGearSet') -> 'Iterable[_5260.AGMAGleasonConicalGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AGMAGleasonConicalGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_AGMA_GLEASON_CONICAL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5260.AGMAGleasonConicalGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_differential_gear(self, design_entity: '_2255.BevelDifferentialGear') -> 'Iterable[_5265.BevelDifferentialGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelDifferentialGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_DIFFERENTIAL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5265.BevelDifferentialGearCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_differential_gear_set(self, design_entity: '_2256.BevelDifferentialGearSet') -> 'Iterable[_5267.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_DIFFERENTIAL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5267.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_differential_planet_gear(self, design_entity: '_2257.BevelDifferentialPlanetGear') -> 'Iterable[_5268.BevelDifferentialPlanetGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelDifferentialPlanetGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_DIFFERENTIAL_PLANET_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5268.BevelDifferentialPlanetGearCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_differential_sun_gear(self, design_entity: '_2258.BevelDifferentialSunGear') -> 'Iterable[_5269.BevelDifferentialSunGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialSunGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelDifferentialSunGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_DIFFERENTIAL_SUN_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5269.BevelDifferentialSunGearCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_gear(self, design_entity: '_2259.BevelGear') -> 'Iterable[_5270.BevelGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5270.BevelGearCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_gear_set(self, design_entity: '_2260.BevelGearSet') -> 'Iterable[_5272.BevelGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5272.BevelGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_conical_gear(self, design_entity: '_2263.ConicalGear') -> 'Iterable[_5286.ConicalGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConicalGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONICAL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5286.ConicalGearCompoundMultibodyDynamicsAnalysis))

    def results_for_conical_gear_set(self, design_entity: '_2264.ConicalGearSet') -> 'Iterable[_5288.ConicalGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConicalGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONICAL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5288.ConicalGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_cylindrical_gear(self, design_entity: '_2265.CylindricalGear') -> 'Iterable[_5301.CylindricalGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CylindricalGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYLINDRICAL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5301.CylindricalGearCompoundMultibodyDynamicsAnalysis))

    def results_for_cylindrical_gear_set(self, design_entity: '_2266.CylindricalGearSet') -> 'Iterable[_5303.CylindricalGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CylindricalGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYLINDRICAL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5303.CylindricalGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_cylindrical_planet_gear(self, design_entity: '_2267.CylindricalPlanetGear') -> 'Iterable[_5304.CylindricalPlanetGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalPlanetGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CylindricalPlanetGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYLINDRICAL_PLANET_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5304.CylindricalPlanetGearCompoundMultibodyDynamicsAnalysis))

    def results_for_gear(self, design_entity: '_2270.Gear') -> 'Iterable[_5312.GearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.Gear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.GearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5312.GearCompoundMultibodyDynamicsAnalysis))

    def results_for_gear_set(self, design_entity: '_2272.GearSet') -> 'Iterable[_5314.GearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.GearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.GearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5314.GearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_hypoid_gear(self, design_entity: '_2274.HypoidGear') -> 'Iterable[_5316.HypoidGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.HypoidGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_HYPOID_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5316.HypoidGearCompoundMultibodyDynamicsAnalysis))

    def results_for_hypoid_gear_set(self, design_entity: '_2275.HypoidGearSet') -> 'Iterable[_5318.HypoidGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.HypoidGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_HYPOID_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5318.HypoidGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_conical_gear(self, design_entity: '_2276.KlingelnbergCycloPalloidConicalGear') -> 'Iterable[_5320.KlingelnbergCycloPalloidConicalGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidConicalGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5320.KlingelnbergCycloPalloidConicalGearCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_conical_gear_set(self, design_entity: '_2277.KlingelnbergCycloPalloidConicalGearSet') -> 'Iterable[_5322.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5322.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_hypoid_gear(self, design_entity: '_2278.KlingelnbergCycloPalloidHypoidGear') -> 'Iterable[_5323.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5323.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_set(self, design_entity: '_2279.KlingelnbergCycloPalloidHypoidGearSet') -> 'Iterable[_5325.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5325.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear(self, design_entity: '_2280.KlingelnbergCycloPalloidSpiralBevelGear') -> 'Iterable[_5326.KlingelnbergCycloPalloidSpiralBevelGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5326.KlingelnbergCycloPalloidSpiralBevelGearCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self, design_entity: '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet') -> 'Iterable[_5328.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5328.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_planetary_gear_set(self, design_entity: '_2282.PlanetaryGearSet') -> 'Iterable[_5338.PlanetaryGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.PlanetaryGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PlanetaryGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PLANETARY_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5338.PlanetaryGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_spiral_bevel_gear(self, design_entity: '_2283.SpiralBevelGear') -> 'Iterable[_5353.SpiralBevelGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpiralBevelGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPIRAL_BEVEL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5353.SpiralBevelGearCompoundMultibodyDynamicsAnalysis))

    def results_for_spiral_bevel_gear_set(self, design_entity: '_2284.SpiralBevelGearSet') -> 'Iterable[_5355.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPIRAL_BEVEL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5355.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_diff_gear(self, design_entity: '_2285.StraightBevelDiffGear') -> 'Iterable[_5359.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_DIFF_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5359.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_diff_gear_set(self, design_entity: '_2286.StraightBevelDiffGearSet') -> 'Iterable[_5361.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_DIFF_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5361.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_gear(self, design_entity: '_2287.StraightBevelGear') -> 'Iterable[_5362.StraightBevelGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5362.StraightBevelGearCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_gear_set(self, design_entity: '_2288.StraightBevelGearSet') -> 'Iterable[_5364.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5364.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_planet_gear(self, design_entity: '_2289.StraightBevelPlanetGear') -> 'Iterable[_5365.StraightBevelPlanetGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelPlanetGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelPlanetGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_PLANET_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5365.StraightBevelPlanetGearCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_sun_gear(self, design_entity: '_2290.StraightBevelSunGear') -> 'Iterable[_5366.StraightBevelSunGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelSunGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelSunGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_SUN_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5366.StraightBevelSunGearCompoundMultibodyDynamicsAnalysis))

    def results_for_worm_gear(self, design_entity: '_2291.WormGear') -> 'Iterable[_5377.WormGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.WormGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_WORM_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5377.WormGearCompoundMultibodyDynamicsAnalysis))

    def results_for_worm_gear_set(self, design_entity: '_2292.WormGearSet') -> 'Iterable[_5379.WormGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.WormGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_WORM_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5379.WormGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_zerol_bevel_gear(self, design_entity: '_2293.ZerolBevelGear') -> 'Iterable[_5380.ZerolBevelGearCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGear)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ZerolBevelGearCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ZEROL_BEVEL_GEAR](design_entity.wrapped if design_entity else None), constructor.new(_5380.ZerolBevelGearCompoundMultibodyDynamicsAnalysis))

    def results_for_zerol_bevel_gear_set(self, design_entity: '_2294.ZerolBevelGearSet') -> 'Iterable[_5382.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGearSet)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ZEROL_BEVEL_GEAR_SET](design_entity.wrapped if design_entity else None), constructor.new(_5382.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis))

    def results_for_cycloidal_assembly(self, design_entity: '_2308.CycloidalAssembly') -> 'Iterable[_5297.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYCLOIDAL_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5297.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_cycloidal_disc(self, design_entity: '_2309.CycloidalDisc') -> 'Iterable[_5299.CycloidalDiscCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalDisc)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CycloidalDiscCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYCLOIDAL_DISC](design_entity.wrapped if design_entity else None), constructor.new(_5299.CycloidalDiscCompoundMultibodyDynamicsAnalysis))

    def results_for_ring_pins(self, design_entity: '_2310.RingPins') -> 'Iterable[_5343.RingPinsCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.RingPins)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RingPinsCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_RING_PINS](design_entity.wrapped if design_entity else None), constructor.new(_5343.RingPinsCompoundMultibodyDynamicsAnalysis))

    def results_for_part_to_part_shear_coupling(self, design_entity: '_2328.PartToPartShearCoupling') -> 'Iterable[_5334.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCoupling)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PART_TO_PART_SHEAR_COUPLING](design_entity.wrapped if design_entity else None), constructor.new(_5334.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis))

    def results_for_part_to_part_shear_coupling_half(self, design_entity: '_2329.PartToPartShearCouplingHalf') -> 'Iterable[_5336.PartToPartShearCouplingHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCouplingHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PartToPartShearCouplingHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PART_TO_PART_SHEAR_COUPLING_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5336.PartToPartShearCouplingHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_belt_drive(self, design_entity: '_2316.BeltDrive') -> 'Iterable[_5264.BeltDriveCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.BeltDrive)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BeltDriveCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BELT_DRIVE](design_entity.wrapped if design_entity else None), constructor.new(_5264.BeltDriveCompoundMultibodyDynamicsAnalysis))

    def results_for_clutch(self, design_entity: '_2318.Clutch') -> 'Iterable[_5275.ClutchCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Clutch)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ClutchCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CLUTCH](design_entity.wrapped if design_entity else None), constructor.new(_5275.ClutchCompoundMultibodyDynamicsAnalysis))

    def results_for_clutch_half(self, design_entity: '_2319.ClutchHalf') -> 'Iterable[_5277.ClutchHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ClutchHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ClutchHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CLUTCH_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5277.ClutchHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_coupling(self, design_entity: '_2321.ConceptCoupling') -> 'Iterable[_5280.ConceptCouplingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCoupling)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptCouplingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_COUPLING](design_entity.wrapped if design_entity else None), constructor.new(_5280.ConceptCouplingCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_coupling_half(self, design_entity: '_2322.ConceptCouplingHalf') -> 'Iterable[_5282.ConceptCouplingHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCouplingHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptCouplingHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_COUPLING_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5282.ConceptCouplingHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_coupling(self, design_entity: '_2323.Coupling') -> 'Iterable[_5291.CouplingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Coupling)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CouplingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_COUPLING](design_entity.wrapped if design_entity else None), constructor.new(_5291.CouplingCompoundMultibodyDynamicsAnalysis))

    def results_for_coupling_half(self, design_entity: '_2324.CouplingHalf') -> 'Iterable[_5293.CouplingHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CouplingHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CouplingHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_COUPLING_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5293.CouplingHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_cvt(self, design_entity: '_2326.CVT') -> 'Iterable[_5295.CVTCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVT)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CVTCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CVT](design_entity.wrapped if design_entity else None), constructor.new(_5295.CVTCompoundMultibodyDynamicsAnalysis))

    def results_for_cvt_pulley(self, design_entity: '_2327.CVTPulley') -> 'Iterable[_5296.CVTPulleyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVTPulley)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CVTPulleyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CVT_PULLEY](design_entity.wrapped if design_entity else None), constructor.new(_5296.CVTPulleyCompoundMultibodyDynamicsAnalysis))

    def results_for_pulley(self, design_entity: '_2330.Pulley') -> 'Iterable[_5342.PulleyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Pulley)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PulleyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PULLEY](design_entity.wrapped if design_entity else None), constructor.new(_5342.PulleyCompoundMultibodyDynamicsAnalysis))

    def results_for_shaft_hub_connection(self, design_entity: '_2338.ShaftHubConnection') -> 'Iterable[_5350.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ShaftHubConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SHAFT_HUB_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5350.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_rolling_ring(self, design_entity: '_2336.RollingRing') -> 'Iterable[_5346.RollingRingCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRing)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RollingRingCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ROLLING_RING](design_entity.wrapped if design_entity else None), constructor.new(_5346.RollingRingCompoundMultibodyDynamicsAnalysis))

    def results_for_rolling_ring_assembly(self, design_entity: '_2337.RollingRingAssembly') -> 'Iterable[_5345.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRingAssembly)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ROLLING_RING_ASSEMBLY](design_entity.wrapped if design_entity else None), constructor.new(_5345.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis))

    def results_for_spring_damper(self, design_entity: '_2340.SpringDamper') -> 'Iterable[_5356.SpringDamperCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamper)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpringDamperCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPRING_DAMPER](design_entity.wrapped if design_entity else None), constructor.new(_5356.SpringDamperCompoundMultibodyDynamicsAnalysis))

    def results_for_spring_damper_half(self, design_entity: '_2341.SpringDamperHalf') -> 'Iterable[_5358.SpringDamperHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamperHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpringDamperHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPRING_DAMPER_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5358.SpringDamperHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_synchroniser(self, design_entity: '_2342.Synchroniser') -> 'Iterable[_5367.SynchroniserCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Synchroniser)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SynchroniserCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SYNCHRONISER](design_entity.wrapped if design_entity else None), constructor.new(_5367.SynchroniserCompoundMultibodyDynamicsAnalysis))

    def results_for_synchroniser_half(self, design_entity: '_2344.SynchroniserHalf') -> 'Iterable[_5368.SynchroniserHalfCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserHalf)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SynchroniserHalfCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SYNCHRONISER_HALF](design_entity.wrapped if design_entity else None), constructor.new(_5368.SynchroniserHalfCompoundMultibodyDynamicsAnalysis))

    def results_for_synchroniser_part(self, design_entity: '_2345.SynchroniserPart') -> 'Iterable[_5369.SynchroniserPartCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserPart)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SynchroniserPartCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SYNCHRONISER_PART](design_entity.wrapped if design_entity else None), constructor.new(_5369.SynchroniserPartCompoundMultibodyDynamicsAnalysis))

    def results_for_synchroniser_sleeve(self, design_entity: '_2346.SynchroniserSleeve') -> 'Iterable[_5370.SynchroniserSleeveCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserSleeve)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SynchroniserSleeveCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SYNCHRONISER_SLEEVE](design_entity.wrapped if design_entity else None), constructor.new(_5370.SynchroniserSleeveCompoundMultibodyDynamicsAnalysis))

    def results_for_torque_converter(self, design_entity: '_2347.TorqueConverter') -> 'Iterable[_5371.TorqueConverterCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverter)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.TorqueConverterCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_TORQUE_CONVERTER](design_entity.wrapped if design_entity else None), constructor.new(_5371.TorqueConverterCompoundMultibodyDynamicsAnalysis))

    def results_for_torque_converter_pump(self, design_entity: '_2348.TorqueConverterPump') -> 'Iterable[_5373.TorqueConverterPumpCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterPump)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.TorqueConverterPumpCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_TORQUE_CONVERTER_PUMP](design_entity.wrapped if design_entity else None), constructor.new(_5373.TorqueConverterPumpCompoundMultibodyDynamicsAnalysis))

    def results_for_torque_converter_turbine(self, design_entity: '_2350.TorqueConverterTurbine') -> 'Iterable[_5374.TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterTurbine)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_TORQUE_CONVERTER_TURBINE](design_entity.wrapped if design_entity else None), constructor.new(_5374.TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis))

    def results_for_shaft_to_mountable_component_connection(self, design_entity: '_2037.ShaftToMountableComponentConnection') -> 'Iterable[_5351.ShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.ShaftToMountableComponentConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5351.ShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_cvt_belt_connection(self, design_entity: '_2015.CVTBeltConnection') -> 'Iterable[_5294.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CVTBeltConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CVT_BELT_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5294.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_belt_connection(self, design_entity: '_2010.BeltConnection') -> 'Iterable[_5263.BeltConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.BeltConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BeltConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BELT_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5263.BeltConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_coaxial_connection(self, design_entity: '_2011.CoaxialConnection') -> 'Iterable[_5278.CoaxialConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CoaxialConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CoaxialConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_COAXIAL_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5278.CoaxialConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_connection(self, design_entity: '_2014.Connection') -> 'Iterable[_5289.ConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.Connection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5289.ConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_inter_mountable_component_connection(self, design_entity: '_2023.InterMountableComponentConnection') -> 'Iterable[_5319.InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.InterMountableComponentConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_INTER_MOUNTABLE_COMPONENT_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5319.InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_planetary_connection(self, design_entity: '_2029.PlanetaryConnection') -> 'Iterable[_5337.PlanetaryConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.PlanetaryConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PlanetaryConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PLANETARY_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5337.PlanetaryConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_rolling_ring_connection(self, design_entity: '_2034.RollingRingConnection') -> 'Iterable[_5347.RollingRingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.RollingRingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RollingRingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ROLLING_RING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5347.RollingRingConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_abstract_shaft_to_mountable_component_connection(self, design_entity: '_2007.AbstractShaftToMountableComponentConnection') -> 'Iterable[_5257.AbstractShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.AbstractShaftToMountableComponentConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AbstractShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5257.AbstractShaftToMountableComponentConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_differential_gear_mesh(self, design_entity: '_2043.BevelDifferentialGearMesh') -> 'Iterable[_5266.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelDifferentialGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_DIFFERENTIAL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5266.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_gear_mesh(self, design_entity: '_2047.ConceptGearMesh') -> 'Iterable[_5284.ConceptGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConceptGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5284.ConceptGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_face_gear_mesh(self, design_entity: '_2053.FaceGearMesh') -> 'Iterable[_5308.FaceGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.FaceGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.FaceGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_FACE_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5308.FaceGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_diff_gear_mesh(self, design_entity: '_2067.StraightBevelDiffGearMesh') -> 'Iterable[_5360.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelDiffGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_DIFF_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5360.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_bevel_gear_mesh(self, design_entity: '_2045.BevelGearMesh') -> 'Iterable[_5271.BevelGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.BevelGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_BEVEL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5271.BevelGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_conical_gear_mesh(self, design_entity: '_2049.ConicalGearMesh') -> 'Iterable[_5287.ConicalGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConicalGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConicalGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONICAL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5287.ConicalGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_agma_gleason_conical_gear_mesh(self, design_entity: '_2041.AGMAGleasonConicalGearMesh') -> 'Iterable[_5259.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.AGMAGleasonConicalGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_AGMA_GLEASON_CONICAL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5259.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_cylindrical_gear_mesh(self, design_entity: '_2051.CylindricalGearMesh') -> 'Iterable[_5302.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.CylindricalGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYLINDRICAL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5302.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_hypoid_gear_mesh(self, design_entity: '_2057.HypoidGearMesh') -> 'Iterable[_5317.HypoidGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.HypoidGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.HypoidGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_HYPOID_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5317.HypoidGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_conical_gear_mesh(self, design_entity: '_2060.KlingelnbergCycloPalloidConicalGearMesh') -> 'Iterable[_5321.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidConicalGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5321.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_mesh(self, design_entity: '_2061.KlingelnbergCycloPalloidHypoidGearMesh') -> 'Iterable[_5324.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidHypoidGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5324.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(self, design_entity: '_2062.KlingelnbergCycloPalloidSpiralBevelGearMesh') -> 'Iterable[_5327.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidSpiralBevelGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5327.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_spiral_bevel_gear_mesh(self, design_entity: '_2065.SpiralBevelGearMesh') -> 'Iterable[_5354.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.SpiralBevelGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_SPIRAL_BEVEL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5354.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_straight_bevel_gear_mesh(self, design_entity: '_2069.StraightBevelGearMesh') -> 'Iterable[_5363.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_STRAIGHT_BEVEL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5363.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_worm_gear_mesh(self, design_entity: '_2071.WormGearMesh') -> 'Iterable[_5378.WormGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.WormGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.WormGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_WORM_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5378.WormGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_zerol_bevel_gear_mesh(self, design_entity: '_2073.ZerolBevelGearMesh') -> 'Iterable[_5381.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ZerolBevelGearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_ZEROL_BEVEL_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5381.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_gear_mesh(self, design_entity: '_2055.GearMesh') -> 'Iterable[_5313.GearMeshCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.GearMesh)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.GearMeshCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_GEAR_MESH](design_entity.wrapped if design_entity else None), constructor.new(_5313.GearMeshCompoundMultibodyDynamicsAnalysis))

    def results_for_cycloidal_disc_central_bearing_connection(self, design_entity: '_2077.CycloidalDiscCentralBearingConnection') -> 'Iterable[_5298.CycloidalDiscCentralBearingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscCentralBearingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CycloidalDiscCentralBearingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5298.CycloidalDiscCentralBearingConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_cycloidal_disc_planetary_bearing_connection(self, design_entity: '_2080.CycloidalDiscPlanetaryBearingConnection') -> 'Iterable[_5300.CycloidalDiscPlanetaryBearingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscPlanetaryBearingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CycloidalDiscPlanetaryBearingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5300.CycloidalDiscPlanetaryBearingConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_ring_pins_to_disc_connection(self, design_entity: '_2083.RingPinsToDiscConnection') -> 'Iterable[_5344.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.RingPinsToDiscConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_RING_PINS_TO_DISC_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5344.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_part_to_part_shear_coupling_connection(self, design_entity: '_2090.PartToPartShearCouplingConnection') -> 'Iterable[_5335.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.PartToPartShearCouplingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_PART_TO_PART_SHEAR_COUPLING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5335.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_clutch_connection(self, design_entity: '_2084.ClutchConnection') -> 'Iterable[_5276.ClutchConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ClutchConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ClutchConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CLUTCH_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5276.ClutchConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_concept_coupling_connection(self, design_entity: '_2086.ConceptCouplingConnection') -> 'Iterable[_5281.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ConceptCouplingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_CONCEPT_COUPLING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5281.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis))

    def results_for_coupling_connection(self, design_entity: '_2088.CouplingConnection') -> 'Iterable[_5292.CouplingConnectionCompoundMultibodyDynamicsAnalysis]':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.CouplingConnection)

        Returns:
            Iterable[mastapy.system_model.analyses_and_results.mbd_analyses.compound.CouplingConnectionCompoundMultibodyDynamicsAnalysis]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.ResultsFor.Overloads[_COUPLING_CONNECTION](design_entity.wrapped if design_entity else None), constructor.new(_5292.CouplingConnectionCompoundMultibodyDynamicsAnalysis))
