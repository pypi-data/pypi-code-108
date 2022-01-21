'''_2176.py

Assembly
'''


from typing import List, TypeVar, Optional

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import (
    _2206, _2186, _2182, _2185,
    _2194, _2213, _2212, _2207,
    _2209, _2177, _2178, _2179,
    _2184, _2189, _2190, _2193,
    _2195, _2196, _2203, _2204,
    _2205, _2210, _2215, _2217,
    _2218, _2220
)
from mastapy.system_model.part_model.gears import (
    _2288, _2275, _2284, _2272,
    _2266, _2264, _2269, _2292,
    _2277, _2253, _2254, _2255,
    _2256, _2257, _2258, _2259,
    _2260, _2261, _2262, _2263,
    _2265, _2267, _2268, _2270,
    _2274, _2276, _2278, _2279,
    _2280, _2281, _2282, _2283,
    _2285, _2286, _2287, _2289,
    _2290, _2291, _2293, _2294
)
from mastapy.system_model.part_model.couplings import (
    _2338, _2316, _2318, _2319,
    _2321, _2322, _2323, _2324,
    _2326, _2327, _2328, _2329,
    _2330, _2336, _2337, _2340,
    _2341, _2342, _2344, _2345,
    _2346, _2347, _2348, _2350
)
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.cycloidal import _2308, _2309, _2310
from mastapy.bearings import _1628, _1653
from mastapy.nodal_analysis import _74
from mastapy.system_model.part_model.creation_options import (
    _2311, _2314, _2315, _2313,
    _2312
)
from mastapy.gears.gear_designs.creation_options import _1093, _1096
from mastapy._internal.python_net import python_net_import
from mastapy.gears import _299
from mastapy.gears.gear_designs.bevel import _1126

_ARRAY = python_net_import('System', 'Array')
_STRING = python_net_import('System', 'String')
_DOUBLE = python_net_import('System', 'Double')
_INT_32 = python_net_import('System', 'Int32')
_ROLLING_BEARING_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'RollingBearingType')
_SPIRAL_BEVEL_GEAR_SET_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.CreationOptions', 'SpiralBevelGearSetCreationOptions')
_CYLINDRICAL_GEAR_PAIR_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.CreationOptions', 'CylindricalGearPairCreationOptions')
_AGMA_GLEASON_CONICAL_GEAR_GEOMETRY_METHODS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'AGMAGleasonConicalGearGeometryMethods')
_BELT_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.CreationOptions', 'BeltCreationOptions')
_PLANET_CARRIER_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.CreationOptions', 'PlanetCarrierCreationOptions')
_SHAFT_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.CreationOptions', 'ShaftCreationOptions')
_CYLINDRICAL_GEAR_LINEAR_TRAIN_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.CreationOptions', 'CylindricalGearLinearTrainCreationOptions')
_CYCLOIDAL_ASSEMBLY_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.CreationOptions', 'CycloidalAssemblyCreationOptions')
_HAND = python_net_import('SMT.MastaAPI.Gears', 'Hand')
_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Assembly')


__docformat__ = 'restructuredtext en'
__all__ = ('Assembly',)


class Assembly(_2177.AbstractAssembly):
    '''Assembly

    This is a mastapy class.
    '''

    TYPE = _ASSEMBLY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Assembly.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_of_widest_cylindrical_gear(self) -> 'float':
        '''float: 'FaceWidthOfWidestCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthOfWidestCylindricalGear

    @property
    def mass_of_gears(self) -> 'float':
        '''float: 'MassOfGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfGears

    @property
    def mass_of_bearings(self) -> 'float':
        '''float: 'MassOfBearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfBearings

    @property
    def mass_of_shafts(self) -> 'float':
        '''float: 'MassOfShafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfShafts

    @property
    def mass_of_fe_part_shafts(self) -> 'float':
        '''float: 'MassOfFEPartShafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfFEPartShafts

    @property
    def mass_of_fe_part_housings(self) -> 'float':
        '''float: 'MassOfFEPartHousings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfFEPartHousings

    @property
    def mass_of_other_parts(self) -> 'float':
        '''float: 'MassOfOtherParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfOtherParts

    @property
    def smallest_number_of_teeth(self) -> 'int':
        '''int: 'SmallestNumberOfTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SmallestNumberOfTeeth

    @property
    def largest_number_of_teeth(self) -> 'int':
        '''int: 'LargestNumberOfTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LargestNumberOfTeeth

    @property
    def transverse_and_axial_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'TransverseAndAxialContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseAndAxialContactRatioRatingForNVH

    @property
    def transverse_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'TransverseContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatioRatingForNVH

    @property
    def axial_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'AxialContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialContactRatioRatingForNVH

    @property
    def minimum_tip_thickness(self) -> 'float':
        '''float: 'MinimumTipThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumTipThickness

    @property
    def oil_level_specification(self) -> '_2206.OilLevelSpecification':
        '''OilLevelSpecification: 'OilLevelSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2206.OilLevelSpecification)(self.wrapped.OilLevelSpecification) if self.wrapped.OilLevelSpecification is not None else None

    @property
    def components_with_unknown_scalar_mass(self) -> 'List[_2186.Component]':
        '''List[Component]: 'ComponentsWithUnknownScalarMass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentsWithUnknownScalarMass, constructor.new(_2186.Component))
        return value

    @property
    def straight_bevel_gear_sets(self) -> 'List[_2288.StraightBevelGearSet]':
        '''List[StraightBevelGearSet]: 'StraightBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearSets, constructor.new(_2288.StraightBevelGearSet))
        return value

    @property
    def hypoid_gear_sets(self) -> 'List[_2275.HypoidGearSet]':
        '''List[HypoidGearSet]: 'HypoidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearSets, constructor.new(_2275.HypoidGearSet))
        return value

    @property
    def spiral_bevel_gear_sets(self) -> 'List[_2284.SpiralBevelGearSet]':
        '''List[SpiralBevelGearSet]: 'SpiralBevelGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpiralBevelGearSets, constructor.new(_2284.SpiralBevelGearSet))
        return value

    @property
    def shaft_hub_connections(self) -> 'List[_2338.ShaftHubConnection]':
        '''List[ShaftHubConnection]: 'ShaftHubConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftHubConnections, constructor.new(_2338.ShaftHubConnection))
        return value

    @property
    def gear_sets(self) -> 'List[_2272.GearSet]':
        '''List[GearSet]: 'GearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSets, constructor.new(_2272.GearSet))
        return value

    @property
    def cylindrical_gear_sets(self) -> 'List[_2266.CylindricalGearSet]':
        '''List[CylindricalGearSet]: 'CylindricalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearSets, constructor.new(_2266.CylindricalGearSet))
        return value

    @property
    def conical_gear_sets(self) -> 'List[_2264.ConicalGearSet]':
        '''List[ConicalGearSet]: 'ConicalGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConicalGearSets, constructor.new(_2264.ConicalGearSet))
        return value

    @property
    def face_gear_sets(self) -> 'List[_2269.FaceGearSet]':
        '''List[FaceGearSet]: 'FaceGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearSets, constructor.new(_2269.FaceGearSet))
        return value

    @property
    def worm_gear_sets(self) -> 'List[_2292.WormGearSet]':
        '''List[WormGearSet]: 'WormGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearSets, constructor.new(_2292.WormGearSet))
        return value

    @property
    def klingelnberg_cyclo_palloid_gear_sets(self) -> 'List[_2277.KlingelnbergCycloPalloidConicalGearSet]':
        '''List[KlingelnbergCycloPalloidConicalGearSet]: 'KlingelnbergCycloPalloidGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidGearSets, constructor.new(_2277.KlingelnbergCycloPalloidConicalGearSet))
        return value

    @property
    def shafts(self) -> 'List[_2223.Shaft]':
        '''List[Shaft]: 'Shafts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shafts, constructor.new(_2223.Shaft))
        return value

    @property
    def bearings(self) -> 'List[_2182.Bearing]':
        '''List[Bearing]: 'Bearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bearings, constructor.new(_2182.Bearing))
        return value

    @property
    def bolted_joints(self) -> 'List[_2185.BoltedJoint]':
        '''List[BoltedJoint]: 'BoltedJoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltedJoints, constructor.new(_2185.BoltedJoint))
        return value

    @property
    def fe_parts(self) -> 'List[_2194.FEPart]':
        '''List[FEPart]: 'FEParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FEParts, constructor.new(_2194.FEPart))
        return value

    @property
    def component_details(self) -> 'List[_2186.Component]':
        '''List[Component]: 'ComponentDetails' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentDetails, constructor.new(_2186.Component))
        return value

    @property
    def power_loads(self) -> 'List[_2213.PowerLoad]':
        '''List[PowerLoad]: 'PowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PowerLoads, constructor.new(_2213.PowerLoad))
        return value

    @property
    def point_loads(self) -> 'List[_2212.PointLoad]':
        '''List[PointLoad]: 'PointLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointLoads, constructor.new(_2212.PointLoad))
        return value

    @property
    def oil_seals(self) -> 'List[_2207.OilSeal]':
        '''List[OilSeal]: 'OilSeals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OilSeals, constructor.new(_2207.OilSeal))
        return value

    def get_part_named(self, name: 'str') -> '_2209.Part':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Part
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2209.Part.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_assembly(self, name: 'str') -> 'Assembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Assembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[Assembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_abstract_assembly(self, name: 'str') -> '_2177.AbstractAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.AbstractAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2177.AbstractAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_abstract_shaft(self, name: 'str') -> '_2178.AbstractShaft':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.AbstractShaft
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2178.AbstractShaft.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_abstract_shaft_or_housing(self, name: 'str') -> '_2179.AbstractShaftOrHousing':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.AbstractShaftOrHousing
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2179.AbstractShaftOrHousing.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bearing(self, name: 'str') -> '_2182.Bearing':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2182.Bearing.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bolt(self, name: 'str') -> '_2184.Bolt':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Bolt
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2184.Bolt.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bolted_joint(self, name: 'str') -> '_2185.BoltedJoint':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.BoltedJoint
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2185.BoltedJoint.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_component(self, name: 'str') -> '_2186.Component':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Component
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2186.Component.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_connector(self, name: 'str') -> '_2189.Connector':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Connector
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2189.Connector.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_datum(self, name: 'str') -> '_2190.Datum':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Datum
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2190.Datum.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_external_cad_model(self, name: 'str') -> '_2193.ExternalCADModel':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.ExternalCADModel
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2193.ExternalCADModel.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_fe_part(self, name: 'str') -> '_2194.FEPart':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.FEPart
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2194.FEPart.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_flexible_pin_assembly(self, name: 'str') -> '_2195.FlexiblePinAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.FlexiblePinAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2195.FlexiblePinAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_guide_dxf_model(self, name: 'str') -> '_2196.GuideDxfModel':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.GuideDxfModel
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2196.GuideDxfModel.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_mass_disc(self, name: 'str') -> '_2203.MassDisc':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.MassDisc
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2203.MassDisc.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_measurement_component(self, name: 'str') -> '_2204.MeasurementComponent':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.MeasurementComponent
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2204.MeasurementComponent.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_mountable_component(self, name: 'str') -> '_2205.MountableComponent':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.MountableComponent
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2205.MountableComponent.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_oil_seal(self, name: 'str') -> '_2207.OilSeal':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.OilSeal
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2207.OilSeal.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_planet_carrier(self, name: 'str') -> '_2210.PlanetCarrier':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.PlanetCarrier
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2210.PlanetCarrier.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_point_load(self, name: 'str') -> '_2212.PointLoad':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.PointLoad
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2212.PointLoad.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_power_load(self, name: 'str') -> '_2213.PowerLoad':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.PowerLoad
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2213.PowerLoad.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_root_assembly(self, name: 'str') -> '_2215.RootAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.RootAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2215.RootAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_specialised_assembly(self, name: 'str') -> '_2217.SpecialisedAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.SpecialisedAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2217.SpecialisedAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_unbalanced_mass(self, name: 'str') -> '_2218.UnbalancedMass':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.UnbalancedMass
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2218.UnbalancedMass.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_virtual_component(self, name: 'str') -> '_2220.VirtualComponent':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.VirtualComponent
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2220.VirtualComponent.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_shaft(self, name: 'str') -> '_2223.Shaft':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.shaft_model.Shaft
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2223.Shaft.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_agma_gleason_conical_gear(self, name: 'str') -> '_2253.AGMAGleasonConicalGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.AGMAGleasonConicalGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2253.AGMAGleasonConicalGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_agma_gleason_conical_gear_set(self, name: 'str') -> '_2254.AGMAGleasonConicalGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2254.AGMAGleasonConicalGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_differential_gear(self, name: 'str') -> '_2255.BevelDifferentialGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2255.BevelDifferentialGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_differential_gear_set(self, name: 'str') -> '_2256.BevelDifferentialGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2256.BevelDifferentialGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_differential_planet_gear(self, name: 'str') -> '_2257.BevelDifferentialPlanetGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2257.BevelDifferentialPlanetGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_differential_sun_gear(self, name: 'str') -> '_2258.BevelDifferentialSunGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialSunGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2258.BevelDifferentialSunGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_gear(self, name: 'str') -> '_2259.BevelGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2259.BevelGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_bevel_gear_set(self, name: 'str') -> '_2260.BevelGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.BevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2260.BevelGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_concept_gear(self, name: 'str') -> '_2261.ConceptGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ConceptGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2261.ConceptGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_concept_gear_set(self, name: 'str') -> '_2262.ConceptGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ConceptGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2262.ConceptGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_conical_gear(self, name: 'str') -> '_2263.ConicalGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ConicalGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2263.ConicalGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_conical_gear_set(self, name: 'str') -> '_2264.ConicalGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ConicalGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2264.ConicalGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cylindrical_gear(self, name: 'str') -> '_2265.CylindricalGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2265.CylindricalGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cylindrical_gear_set(self, name: 'str') -> '_2266.CylindricalGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2266.CylindricalGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cylindrical_planet_gear(self, name: 'str') -> '_2267.CylindricalPlanetGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalPlanetGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2267.CylindricalPlanetGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_face_gear(self, name: 'str') -> '_2268.FaceGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.FaceGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2268.FaceGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_face_gear_set(self, name: 'str') -> '_2269.FaceGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.FaceGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2269.FaceGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_gear(self, name: 'str') -> '_2270.Gear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.Gear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2270.Gear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_gear_set(self, name: 'str') -> '_2272.GearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.GearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2272.GearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_hypoid_gear(self, name: 'str') -> '_2274.HypoidGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.HypoidGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2274.HypoidGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_hypoid_gear_set(self, name: 'str') -> '_2275.HypoidGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.HypoidGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2275.HypoidGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_conical_gear(self, name: 'str') -> '_2276.KlingelnbergCycloPalloidConicalGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2276.KlingelnbergCycloPalloidConicalGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self, name: 'str') -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2277.KlingelnbergCycloPalloidConicalGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self, name: 'str') -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2278.KlingelnbergCycloPalloidHypoidGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self, name: 'str') -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self, name: 'str') -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self, name: 'str') -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_planetary_gear_set(self, name: 'str') -> '_2282.PlanetaryGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.PlanetaryGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2282.PlanetaryGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_spiral_bevel_gear(self, name: 'str') -> '_2283.SpiralBevelGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.SpiralBevelGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2283.SpiralBevelGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_spiral_bevel_gear_set(self, name: 'str') -> '_2284.SpiralBevelGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.SpiralBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2284.SpiralBevelGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_diff_gear(self, name: 'str') -> '_2285.StraightBevelDiffGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelDiffGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2285.StraightBevelDiffGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_diff_gear_set(self, name: 'str') -> '_2286.StraightBevelDiffGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelDiffGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2286.StraightBevelDiffGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_gear(self, name: 'str') -> '_2287.StraightBevelGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2287.StraightBevelGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_gear_set(self, name: 'str') -> '_2288.StraightBevelGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2288.StraightBevelGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_planet_gear(self, name: 'str') -> '_2289.StraightBevelPlanetGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelPlanetGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2289.StraightBevelPlanetGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_straight_bevel_sun_gear(self, name: 'str') -> '_2290.StraightBevelSunGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelSunGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2290.StraightBevelSunGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_worm_gear(self, name: 'str') -> '_2291.WormGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.WormGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2291.WormGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_worm_gear_set(self, name: 'str') -> '_2292.WormGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.WormGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2292.WormGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_zerol_bevel_gear(self, name: 'str') -> '_2293.ZerolBevelGear':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ZerolBevelGear
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2293.ZerolBevelGear.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_zerol_bevel_gear_set(self, name: 'str') -> '_2294.ZerolBevelGearSet':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.gears.ZerolBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2294.ZerolBevelGearSet.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cycloidal_assembly(self, name: 'str') -> '_2308.CycloidalAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.cycloidal.CycloidalAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2308.CycloidalAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cycloidal_disc(self, name: 'str') -> '_2309.CycloidalDisc':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.cycloidal.CycloidalDisc
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2309.CycloidalDisc.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_ring_pins(self, name: 'str') -> '_2310.RingPins':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.cycloidal.RingPins
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2310.RingPins.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_belt_drive(self, name: 'str') -> '_2316.BeltDrive':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.BeltDrive
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2316.BeltDrive.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_clutch(self, name: 'str') -> '_2318.Clutch':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.Clutch
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2318.Clutch.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_clutch_half(self, name: 'str') -> '_2319.ClutchHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.ClutchHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2319.ClutchHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_concept_coupling(self, name: 'str') -> '_2321.ConceptCoupling':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.ConceptCoupling
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2321.ConceptCoupling.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_concept_coupling_half(self, name: 'str') -> '_2322.ConceptCouplingHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.ConceptCouplingHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2322.ConceptCouplingHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_coupling(self, name: 'str') -> '_2323.Coupling':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.Coupling
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2323.Coupling.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_coupling_half(self, name: 'str') -> '_2324.CouplingHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.CouplingHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2324.CouplingHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cvt(self, name: 'str') -> '_2326.CVT':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.CVT
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2326.CVT.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_cvt_pulley(self, name: 'str') -> '_2327.CVTPulley':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.CVTPulley
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2327.CVTPulley.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_part_to_part_shear_coupling(self, name: 'str') -> '_2328.PartToPartShearCoupling':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.PartToPartShearCoupling
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2328.PartToPartShearCoupling.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_part_to_part_shear_coupling_half(self, name: 'str') -> '_2329.PartToPartShearCouplingHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.PartToPartShearCouplingHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2329.PartToPartShearCouplingHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_pulley(self, name: 'str') -> '_2330.Pulley':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.Pulley
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2330.Pulley.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_rolling_ring(self, name: 'str') -> '_2336.RollingRing':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.RollingRing
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2336.RollingRing.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_rolling_ring_assembly(self, name: 'str') -> '_2337.RollingRingAssembly':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.RollingRingAssembly
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2337.RollingRingAssembly.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_shaft_hub_connection(self, name: 'str') -> '_2338.ShaftHubConnection':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.ShaftHubConnection
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2338.ShaftHubConnection.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_spring_damper(self, name: 'str') -> '_2340.SpringDamper':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.SpringDamper
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2340.SpringDamper.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_spring_damper_half(self, name: 'str') -> '_2341.SpringDamperHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.SpringDamperHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2341.SpringDamperHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_synchroniser(self, name: 'str') -> '_2342.Synchroniser':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.Synchroniser
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2342.Synchroniser.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_synchroniser_half(self, name: 'str') -> '_2344.SynchroniserHalf':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.SynchroniserHalf
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2344.SynchroniserHalf.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_synchroniser_part(self, name: 'str') -> '_2345.SynchroniserPart':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.SynchroniserPart
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2345.SynchroniserPart.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_synchroniser_sleeve(self, name: 'str') -> '_2346.SynchroniserSleeve':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.SynchroniserSleeve
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2346.SynchroniserSleeve.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_torque_converter(self, name: 'str') -> '_2347.TorqueConverter':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.TorqueConverter
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2347.TorqueConverter.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_torque_converter_pump(self, name: 'str') -> '_2348.TorqueConverterPump':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.TorqueConverterPump
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2348.TorqueConverterPump.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_part_named_of_type_torque_converter_turbine(self, name: 'str') -> '_2350.TorqueConverterTurbine':
        ''' 'GetPartNamed' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.TorqueConverterTurbine
        '''

        name = str(name)
        method_result = self.wrapped.GetPartNamed[_2350.TorqueConverterTurbine.TYPE](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_part(self, part_type: 'Assembly.PartType', name: 'str') -> '_2209.Part':
        ''' 'AddPart' is the original name of this method.

        Args:
            part_type (mastapy.system_model.part_model.Assembly.PartType)
            name (str)

        Returns:
            mastapy.system_model.part_model.Part
        '''

        part_type = conversion.mp_to_pn_enum(part_type)
        name = str(name)
        method_result = self.wrapped.AddPart(part_type, name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def all_parts(self) -> 'List[_2209.Part]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Part]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2209.Part.TYPE](), constructor.new(_2209.Part))

    def all_parts_of_type_assembly(self) -> 'List[Assembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Assembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[Assembly.TYPE](), constructor.new(Assembly))

    def all_parts_of_type_abstract_assembly(self) -> 'List[_2177.AbstractAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.AbstractAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2177.AbstractAssembly.TYPE](), constructor.new(_2177.AbstractAssembly))

    def all_parts_of_type_abstract_shaft(self) -> 'List[_2178.AbstractShaft]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.AbstractShaft]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2178.AbstractShaft.TYPE](), constructor.new(_2178.AbstractShaft))

    def all_parts_of_type_abstract_shaft_or_housing(self) -> 'List[_2179.AbstractShaftOrHousing]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.AbstractShaftOrHousing]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2179.AbstractShaftOrHousing.TYPE](), constructor.new(_2179.AbstractShaftOrHousing))

    def all_parts_of_type_bearing(self) -> 'List[_2182.Bearing]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Bearing]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2182.Bearing.TYPE](), constructor.new(_2182.Bearing))

    def all_parts_of_type_bolt(self) -> 'List[_2184.Bolt]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Bolt]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2184.Bolt.TYPE](), constructor.new(_2184.Bolt))

    def all_parts_of_type_bolted_joint(self) -> 'List[_2185.BoltedJoint]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.BoltedJoint]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2185.BoltedJoint.TYPE](), constructor.new(_2185.BoltedJoint))

    def all_parts_of_type_component(self) -> 'List[_2186.Component]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Component]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2186.Component.TYPE](), constructor.new(_2186.Component))

    def all_parts_of_type_connector(self) -> 'List[_2189.Connector]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Connector]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2189.Connector.TYPE](), constructor.new(_2189.Connector))

    def all_parts_of_type_datum(self) -> 'List[_2190.Datum]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.Datum]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2190.Datum.TYPE](), constructor.new(_2190.Datum))

    def all_parts_of_type_external_cad_model(self) -> 'List[_2193.ExternalCADModel]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.ExternalCADModel]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2193.ExternalCADModel.TYPE](), constructor.new(_2193.ExternalCADModel))

    def all_parts_of_type_fe_part(self) -> 'List[_2194.FEPart]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.FEPart]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2194.FEPart.TYPE](), constructor.new(_2194.FEPart))

    def all_parts_of_type_flexible_pin_assembly(self) -> 'List[_2195.FlexiblePinAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.FlexiblePinAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2195.FlexiblePinAssembly.TYPE](), constructor.new(_2195.FlexiblePinAssembly))

    def all_parts_of_type_guide_dxf_model(self) -> 'List[_2196.GuideDxfModel]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.GuideDxfModel]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2196.GuideDxfModel.TYPE](), constructor.new(_2196.GuideDxfModel))

    def all_parts_of_type_mass_disc(self) -> 'List[_2203.MassDisc]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.MassDisc]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2203.MassDisc.TYPE](), constructor.new(_2203.MassDisc))

    def all_parts_of_type_measurement_component(self) -> 'List[_2204.MeasurementComponent]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.MeasurementComponent]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2204.MeasurementComponent.TYPE](), constructor.new(_2204.MeasurementComponent))

    def all_parts_of_type_mountable_component(self) -> 'List[_2205.MountableComponent]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.MountableComponent]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2205.MountableComponent.TYPE](), constructor.new(_2205.MountableComponent))

    def all_parts_of_type_oil_seal(self) -> 'List[_2207.OilSeal]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.OilSeal]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2207.OilSeal.TYPE](), constructor.new(_2207.OilSeal))

    def all_parts_of_type_planet_carrier(self) -> 'List[_2210.PlanetCarrier]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.PlanetCarrier]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2210.PlanetCarrier.TYPE](), constructor.new(_2210.PlanetCarrier))

    def all_parts_of_type_point_load(self) -> 'List[_2212.PointLoad]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.PointLoad]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2212.PointLoad.TYPE](), constructor.new(_2212.PointLoad))

    def all_parts_of_type_power_load(self) -> 'List[_2213.PowerLoad]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.PowerLoad]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2213.PowerLoad.TYPE](), constructor.new(_2213.PowerLoad))

    def all_parts_of_type_root_assembly(self) -> 'List[_2215.RootAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.RootAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2215.RootAssembly.TYPE](), constructor.new(_2215.RootAssembly))

    def all_parts_of_type_specialised_assembly(self) -> 'List[_2217.SpecialisedAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.SpecialisedAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2217.SpecialisedAssembly.TYPE](), constructor.new(_2217.SpecialisedAssembly))

    def all_parts_of_type_unbalanced_mass(self) -> 'List[_2218.UnbalancedMass]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.UnbalancedMass]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2218.UnbalancedMass.TYPE](), constructor.new(_2218.UnbalancedMass))

    def all_parts_of_type_virtual_component(self) -> 'List[_2220.VirtualComponent]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.VirtualComponent]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2220.VirtualComponent.TYPE](), constructor.new(_2220.VirtualComponent))

    def all_parts_of_type_shaft(self) -> 'List[_2223.Shaft]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.shaft_model.Shaft]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2223.Shaft.TYPE](), constructor.new(_2223.Shaft))

    def all_parts_of_type_agma_gleason_conical_gear(self) -> 'List[_2253.AGMAGleasonConicalGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.AGMAGleasonConicalGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2253.AGMAGleasonConicalGear.TYPE](), constructor.new(_2253.AGMAGleasonConicalGear))

    def all_parts_of_type_agma_gleason_conical_gear_set(self) -> 'List[_2254.AGMAGleasonConicalGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2254.AGMAGleasonConicalGearSet.TYPE](), constructor.new(_2254.AGMAGleasonConicalGearSet))

    def all_parts_of_type_bevel_differential_gear(self) -> 'List[_2255.BevelDifferentialGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelDifferentialGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2255.BevelDifferentialGear.TYPE](), constructor.new(_2255.BevelDifferentialGear))

    def all_parts_of_type_bevel_differential_gear_set(self) -> 'List[_2256.BevelDifferentialGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelDifferentialGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2256.BevelDifferentialGearSet.TYPE](), constructor.new(_2256.BevelDifferentialGearSet))

    def all_parts_of_type_bevel_differential_planet_gear(self) -> 'List[_2257.BevelDifferentialPlanetGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2257.BevelDifferentialPlanetGear.TYPE](), constructor.new(_2257.BevelDifferentialPlanetGear))

    def all_parts_of_type_bevel_differential_sun_gear(self) -> 'List[_2258.BevelDifferentialSunGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelDifferentialSunGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2258.BevelDifferentialSunGear.TYPE](), constructor.new(_2258.BevelDifferentialSunGear))

    def all_parts_of_type_bevel_gear(self) -> 'List[_2259.BevelGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2259.BevelGear.TYPE](), constructor.new(_2259.BevelGear))

    def all_parts_of_type_bevel_gear_set(self) -> 'List[_2260.BevelGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.BevelGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2260.BevelGearSet.TYPE](), constructor.new(_2260.BevelGearSet))

    def all_parts_of_type_concept_gear(self) -> 'List[_2261.ConceptGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ConceptGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2261.ConceptGear.TYPE](), constructor.new(_2261.ConceptGear))

    def all_parts_of_type_concept_gear_set(self) -> 'List[_2262.ConceptGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ConceptGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2262.ConceptGearSet.TYPE](), constructor.new(_2262.ConceptGearSet))

    def all_parts_of_type_conical_gear(self) -> 'List[_2263.ConicalGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ConicalGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2263.ConicalGear.TYPE](), constructor.new(_2263.ConicalGear))

    def all_parts_of_type_conical_gear_set(self) -> 'List[_2264.ConicalGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ConicalGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2264.ConicalGearSet.TYPE](), constructor.new(_2264.ConicalGearSet))

    def all_parts_of_type_cylindrical_gear(self) -> 'List[_2265.CylindricalGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.CylindricalGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2265.CylindricalGear.TYPE](), constructor.new(_2265.CylindricalGear))

    def all_parts_of_type_cylindrical_gear_set(self) -> 'List[_2266.CylindricalGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.CylindricalGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2266.CylindricalGearSet.TYPE](), constructor.new(_2266.CylindricalGearSet))

    def all_parts_of_type_cylindrical_planet_gear(self) -> 'List[_2267.CylindricalPlanetGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.CylindricalPlanetGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2267.CylindricalPlanetGear.TYPE](), constructor.new(_2267.CylindricalPlanetGear))

    def all_parts_of_type_face_gear(self) -> 'List[_2268.FaceGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.FaceGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2268.FaceGear.TYPE](), constructor.new(_2268.FaceGear))

    def all_parts_of_type_face_gear_set(self) -> 'List[_2269.FaceGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.FaceGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2269.FaceGearSet.TYPE](), constructor.new(_2269.FaceGearSet))

    def all_parts_of_type_gear(self) -> 'List[_2270.Gear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.Gear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2270.Gear.TYPE](), constructor.new(_2270.Gear))

    def all_parts_of_type_gear_set(self) -> 'List[_2272.GearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.GearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2272.GearSet.TYPE](), constructor.new(_2272.GearSet))

    def all_parts_of_type_hypoid_gear(self) -> 'List[_2274.HypoidGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.HypoidGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2274.HypoidGear.TYPE](), constructor.new(_2274.HypoidGear))

    def all_parts_of_type_hypoid_gear_set(self) -> 'List[_2275.HypoidGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.HypoidGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2275.HypoidGearSet.TYPE](), constructor.new(_2275.HypoidGearSet))

    def all_parts_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> 'List[_2276.KlingelnbergCycloPalloidConicalGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2276.KlingelnbergCycloPalloidConicalGear.TYPE](), constructor.new(_2276.KlingelnbergCycloPalloidConicalGear))

    def all_parts_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> 'List[_2277.KlingelnbergCycloPalloidConicalGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2277.KlingelnbergCycloPalloidConicalGearSet.TYPE](), constructor.new(_2277.KlingelnbergCycloPalloidConicalGearSet))

    def all_parts_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> 'List[_2278.KlingelnbergCycloPalloidHypoidGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2278.KlingelnbergCycloPalloidHypoidGear.TYPE](), constructor.new(_2278.KlingelnbergCycloPalloidHypoidGear))

    def all_parts_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> 'List[_2279.KlingelnbergCycloPalloidHypoidGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE](), constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet))

    def all_parts_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> 'List[_2280.KlingelnbergCycloPalloidSpiralBevelGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE](), constructor.new(_2280.KlingelnbergCycloPalloidSpiralBevelGear))

    def all_parts_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> 'List[_2281.KlingelnbergCycloPalloidSpiralBevelGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE](), constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet))

    def all_parts_of_type_planetary_gear_set(self) -> 'List[_2282.PlanetaryGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.PlanetaryGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2282.PlanetaryGearSet.TYPE](), constructor.new(_2282.PlanetaryGearSet))

    def all_parts_of_type_spiral_bevel_gear(self) -> 'List[_2283.SpiralBevelGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.SpiralBevelGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2283.SpiralBevelGear.TYPE](), constructor.new(_2283.SpiralBevelGear))

    def all_parts_of_type_spiral_bevel_gear_set(self) -> 'List[_2284.SpiralBevelGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.SpiralBevelGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2284.SpiralBevelGearSet.TYPE](), constructor.new(_2284.SpiralBevelGearSet))

    def all_parts_of_type_straight_bevel_diff_gear(self) -> 'List[_2285.StraightBevelDiffGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelDiffGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2285.StraightBevelDiffGear.TYPE](), constructor.new(_2285.StraightBevelDiffGear))

    def all_parts_of_type_straight_bevel_diff_gear_set(self) -> 'List[_2286.StraightBevelDiffGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelDiffGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2286.StraightBevelDiffGearSet.TYPE](), constructor.new(_2286.StraightBevelDiffGearSet))

    def all_parts_of_type_straight_bevel_gear(self) -> 'List[_2287.StraightBevelGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2287.StraightBevelGear.TYPE](), constructor.new(_2287.StraightBevelGear))

    def all_parts_of_type_straight_bevel_gear_set(self) -> 'List[_2288.StraightBevelGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2288.StraightBevelGearSet.TYPE](), constructor.new(_2288.StraightBevelGearSet))

    def all_parts_of_type_straight_bevel_planet_gear(self) -> 'List[_2289.StraightBevelPlanetGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelPlanetGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2289.StraightBevelPlanetGear.TYPE](), constructor.new(_2289.StraightBevelPlanetGear))

    def all_parts_of_type_straight_bevel_sun_gear(self) -> 'List[_2290.StraightBevelSunGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.StraightBevelSunGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2290.StraightBevelSunGear.TYPE](), constructor.new(_2290.StraightBevelSunGear))

    def all_parts_of_type_worm_gear(self) -> 'List[_2291.WormGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.WormGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2291.WormGear.TYPE](), constructor.new(_2291.WormGear))

    def all_parts_of_type_worm_gear_set(self) -> 'List[_2292.WormGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.WormGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2292.WormGearSet.TYPE](), constructor.new(_2292.WormGearSet))

    def all_parts_of_type_zerol_bevel_gear(self) -> 'List[_2293.ZerolBevelGear]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ZerolBevelGear]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2293.ZerolBevelGear.TYPE](), constructor.new(_2293.ZerolBevelGear))

    def all_parts_of_type_zerol_bevel_gear_set(self) -> 'List[_2294.ZerolBevelGearSet]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.gears.ZerolBevelGearSet]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2294.ZerolBevelGearSet.TYPE](), constructor.new(_2294.ZerolBevelGearSet))

    def all_parts_of_type_cycloidal_assembly(self) -> 'List[_2308.CycloidalAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.cycloidal.CycloidalAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2308.CycloidalAssembly.TYPE](), constructor.new(_2308.CycloidalAssembly))

    def all_parts_of_type_cycloidal_disc(self) -> 'List[_2309.CycloidalDisc]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.cycloidal.CycloidalDisc]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2309.CycloidalDisc.TYPE](), constructor.new(_2309.CycloidalDisc))

    def all_parts_of_type_ring_pins(self) -> 'List[_2310.RingPins]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.cycloidal.RingPins]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2310.RingPins.TYPE](), constructor.new(_2310.RingPins))

    def all_parts_of_type_belt_drive(self) -> 'List[_2316.BeltDrive]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.BeltDrive]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2316.BeltDrive.TYPE](), constructor.new(_2316.BeltDrive))

    def all_parts_of_type_clutch(self) -> 'List[_2318.Clutch]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.Clutch]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2318.Clutch.TYPE](), constructor.new(_2318.Clutch))

    def all_parts_of_type_clutch_half(self) -> 'List[_2319.ClutchHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.ClutchHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2319.ClutchHalf.TYPE](), constructor.new(_2319.ClutchHalf))

    def all_parts_of_type_concept_coupling(self) -> 'List[_2321.ConceptCoupling]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.ConceptCoupling]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2321.ConceptCoupling.TYPE](), constructor.new(_2321.ConceptCoupling))

    def all_parts_of_type_concept_coupling_half(self) -> 'List[_2322.ConceptCouplingHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.ConceptCouplingHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2322.ConceptCouplingHalf.TYPE](), constructor.new(_2322.ConceptCouplingHalf))

    def all_parts_of_type_coupling(self) -> 'List[_2323.Coupling]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.Coupling]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2323.Coupling.TYPE](), constructor.new(_2323.Coupling))

    def all_parts_of_type_coupling_half(self) -> 'List[_2324.CouplingHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.CouplingHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2324.CouplingHalf.TYPE](), constructor.new(_2324.CouplingHalf))

    def all_parts_of_type_cvt(self) -> 'List[_2326.CVT]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.CVT]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2326.CVT.TYPE](), constructor.new(_2326.CVT))

    def all_parts_of_type_cvt_pulley(self) -> 'List[_2327.CVTPulley]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.CVTPulley]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2327.CVTPulley.TYPE](), constructor.new(_2327.CVTPulley))

    def all_parts_of_type_part_to_part_shear_coupling(self) -> 'List[_2328.PartToPartShearCoupling]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.PartToPartShearCoupling]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2328.PartToPartShearCoupling.TYPE](), constructor.new(_2328.PartToPartShearCoupling))

    def all_parts_of_type_part_to_part_shear_coupling_half(self) -> 'List[_2329.PartToPartShearCouplingHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.PartToPartShearCouplingHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2329.PartToPartShearCouplingHalf.TYPE](), constructor.new(_2329.PartToPartShearCouplingHalf))

    def all_parts_of_type_pulley(self) -> 'List[_2330.Pulley]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.Pulley]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2330.Pulley.TYPE](), constructor.new(_2330.Pulley))

    def all_parts_of_type_rolling_ring(self) -> 'List[_2336.RollingRing]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.RollingRing]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2336.RollingRing.TYPE](), constructor.new(_2336.RollingRing))

    def all_parts_of_type_rolling_ring_assembly(self) -> 'List[_2337.RollingRingAssembly]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.RollingRingAssembly]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2337.RollingRingAssembly.TYPE](), constructor.new(_2337.RollingRingAssembly))

    def all_parts_of_type_shaft_hub_connection(self) -> 'List[_2338.ShaftHubConnection]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.ShaftHubConnection]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2338.ShaftHubConnection.TYPE](), constructor.new(_2338.ShaftHubConnection))

    def all_parts_of_type_spring_damper(self) -> 'List[_2340.SpringDamper]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.SpringDamper]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2340.SpringDamper.TYPE](), constructor.new(_2340.SpringDamper))

    def all_parts_of_type_spring_damper_half(self) -> 'List[_2341.SpringDamperHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.SpringDamperHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2341.SpringDamperHalf.TYPE](), constructor.new(_2341.SpringDamperHalf))

    def all_parts_of_type_synchroniser(self) -> 'List[_2342.Synchroniser]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.Synchroniser]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2342.Synchroniser.TYPE](), constructor.new(_2342.Synchroniser))

    def all_parts_of_type_synchroniser_half(self) -> 'List[_2344.SynchroniserHalf]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.SynchroniserHalf]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2344.SynchroniserHalf.TYPE](), constructor.new(_2344.SynchroniserHalf))

    def all_parts_of_type_synchroniser_part(self) -> 'List[_2345.SynchroniserPart]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.SynchroniserPart]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2345.SynchroniserPart.TYPE](), constructor.new(_2345.SynchroniserPart))

    def all_parts_of_type_synchroniser_sleeve(self) -> 'List[_2346.SynchroniserSleeve]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.SynchroniserSleeve]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2346.SynchroniserSleeve.TYPE](), constructor.new(_2346.SynchroniserSleeve))

    def all_parts_of_type_torque_converter(self) -> 'List[_2347.TorqueConverter]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.TorqueConverter]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2347.TorqueConverter.TYPE](), constructor.new(_2347.TorqueConverter))

    def all_parts_of_type_torque_converter_pump(self) -> 'List[_2348.TorqueConverterPump]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.TorqueConverterPump]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2348.TorqueConverterPump.TYPE](), constructor.new(_2348.TorqueConverterPump))

    def all_parts_of_type_torque_converter_turbine(self) -> 'List[_2350.TorqueConverterTurbine]':
        ''' 'AllParts' is the original name of this method.

        Returns:
            List[mastapy.system_model.part_model.couplings.TorqueConverterTurbine]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.AllParts[_2350.TorqueConverterTurbine.TYPE](), constructor.new(_2350.TorqueConverterTurbine))

    def add_rolling_bearing_from_catalogue(self, catalogue: '_1628.BearingCatalog', designation: 'str', name: 'str') -> '_2182.Bearing':
        ''' 'AddRollingBearingFromCatalogue' is the original name of this method.

        Args:
            catalogue (mastapy.bearings.BearingCatalog)
            designation (str)
            name (str)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        catalogue = conversion.mp_to_pn_enum(catalogue)
        designation = str(designation)
        name = str(name)
        method_result = self.wrapped.AddRollingBearingFromCatalogue(catalogue, designation if designation else '', name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_bearing_with_name_and_rolling_bearing_type(self, name: 'str', type_: '_1653.RollingBearingType') -> '_2182.Bearing':
        ''' 'AddBearing' is the original name of this method.

        Args:
            name (str)
            type_ (mastapy.bearings.RollingBearingType)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        type_ = conversion.mp_to_pn_enum(type_)
        method_result = self.wrapped.AddBearing.Overloads[_STRING, _ROLLING_BEARING_TYPE](name if name else '', type_)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_bearing_with_name_rolling_bearing_type_and_designation(self, name: 'str', type_: '_1653.RollingBearingType', designation: 'str') -> '_2182.Bearing':
        ''' 'AddBearing' is the original name of this method.

        Args:
            name (str)
            type_ (mastapy.bearings.RollingBearingType)
            designation (str)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        type_ = conversion.mp_to_pn_enum(type_)
        designation = str(designation)
        method_result = self.wrapped.AddBearing.Overloads[_STRING, _ROLLING_BEARING_TYPE, _STRING](name if name else '', type_, designation if designation else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_linear_bearing(self, name: 'str', width: 'float') -> '_2182.Bearing':
        ''' 'AddLinearBearing' is the original name of this method.

        Args:
            name (str)
            width (float)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        width = float(width)
        method_result = self.wrapped.AddLinearBearing(name if name else '', width if width else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def import_fe_mesh_from_file(self, file_name: 'str', stiffness_matrix: '_74.NodalMatrix') -> '_2194.FEPart':
        ''' 'ImportFEMeshFromFile' is the original name of this method.

        Args:
            file_name (str)
            stiffness_matrix (mastapy.nodal_analysis.NodalMatrix)

        Returns:
            mastapy.system_model.part_model.FEPart
        '''

        file_name = str(file_name)
        method_result = self.wrapped.ImportFEMeshFromFile(file_name if file_name else '', stiffness_matrix.wrapped if stiffness_matrix else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_assembly(self, name: Optional['str'] = 'Assembly') -> 'Assembly':
        ''' 'AddAssembly' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.Assembly
        '''

        name = str(name)
        method_result = self.wrapped.AddAssembly(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_oil_seal(self, name: Optional['str'] = 'Oil Seal') -> '_2207.OilSeal':
        ''' 'AddOilSeal' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.OilSeal
        '''

        name = str(name)
        method_result = self.wrapped.AddOilSeal(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_power_load(self, name: Optional['str'] = 'Power Load') -> '_2213.PowerLoad':
        ''' 'AddPowerLoad' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.PowerLoad
        '''

        name = str(name)
        method_result = self.wrapped.AddPowerLoad(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_point_load(self, name: Optional['str'] = 'Point Load') -> '_2212.PointLoad':
        ''' 'AddPointLoad' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.PointLoad
        '''

        name = str(name)
        method_result = self.wrapped.AddPointLoad(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_datum(self, name: Optional['str'] = 'Datum') -> '_2190.Datum':
        ''' 'AddDatum' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.Datum
        '''

        name = str(name)
        method_result = self.wrapped.AddDatum(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_imported_fe_component(self, name: Optional['str'] = 'Imported FE') -> '_2194.FEPart':
        ''' 'AddImportedFEComponent' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.FEPart
        '''

        name = str(name)
        method_result = self.wrapped.AddImportedFEComponent(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_measurement_component(self, name: Optional['str'] = 'Measurement Component') -> '_2204.MeasurementComponent':
        ''' 'AddMeasurementComponent' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.MeasurementComponent
        '''

        name = str(name)
        method_result = self.wrapped.AddMeasurementComponent(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_mass_disc(self, name: Optional['str'] = 'Mass Disc') -> '_2203.MassDisc':
        ''' 'AddMassDisc' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.MassDisc
        '''

        name = str(name)
        method_result = self.wrapped.AddMassDisc(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_unbalanced_mass(self, name: Optional['str'] = 'Unbalanced Mass') -> '_2218.UnbalancedMass':
        ''' 'AddUnbalancedMass' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.UnbalancedMass
        '''

        name = str(name)
        method_result = self.wrapped.AddUnbalancedMass(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_straight_bevel_differential_gear_set(self, name: Optional['str'] = 'Straight Bevel Differential Gear Set') -> '_2286.StraightBevelDiffGearSet':
        ''' 'AddStraightBevelDifferentialGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelDiffGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddStraightBevelDifferentialGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_spiral_bevel_differential_gear_set(self, name: Optional['str'] = 'Spiral Bevel Differential Gear Set') -> '_2256.BevelDifferentialGearSet':
        ''' 'AddSpiralBevelDifferentialGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddSpiralBevelDifferentialGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_zerol_bevel_differential_gear_set(self, name: Optional['str'] = 'Zerol Bevel Differential Gear Set') -> '_2256.BevelDifferentialGearSet':
        ''' 'AddZerolBevelDifferentialGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.BevelDifferentialGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddZerolBevelDifferentialGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_planetary_gear_set(self, name: Optional['str'] = 'Planetary Gear Set') -> '_2282.PlanetaryGearSet':
        ''' 'AddPlanetaryGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.PlanetaryGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddPlanetaryGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_spiral_bevel_gear_set(self, name: Optional['str'] = 'Spiral Bevel Gear Set') -> '_2284.SpiralBevelGearSet':
        ''' 'AddSpiralBevelGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.SpiralBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddSpiralBevelGearSet.Overloads[_STRING](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self, name: Optional['str'] = 'Klingelnberg Cyclo Palloid Spiral Bevel Gear Set') -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        ''' 'AddKlingelnbergCycloPalloidSpiralBevelGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddKlingelnbergCycloPalloidSpiralBevelGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_klingelnberg_cyclo_palloid_hypoid_gear_set(self, name: Optional['str'] = 'Klingelnberg Cyclo Palloid Hypoid Gear Set') -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        ''' 'AddKlingelnbergCycloPalloidHypoidGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddKlingelnbergCycloPalloidHypoidGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_straight_bevel_gear_set(self, name: Optional['str'] = 'Straight Bevel Gear Set') -> '_2288.StraightBevelGearSet':
        ''' 'AddStraightBevelGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.StraightBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddStraightBevelGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_hypoid_gear_set(self, name: Optional['str'] = 'Hypoid Gear Set') -> '_2275.HypoidGearSet':
        ''' 'AddHypoidGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.HypoidGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddHypoidGearSet.Overloads[_STRING](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_face_gear_set(self, name: Optional['str'] = 'Face Gear Set') -> '_2269.FaceGearSet':
        ''' 'AddFaceGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.FaceGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddFaceGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_worm_gear_set(self, name: Optional['str'] = 'Worm Gear Set') -> '_2292.WormGearSet':
        ''' 'AddWormGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.WormGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddWormGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_zerol_bevel_gear_set(self, name: Optional['str'] = 'Zerol Bevel Gear Set') -> '_2294.ZerolBevelGearSet':
        ''' 'AddZerolBevelGearSet' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.gears.ZerolBevelGearSet
        '''

        name = str(name)
        method_result = self.wrapped.AddZerolBevelGearSet(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_clutch(self, name: Optional['str'] = 'Clutch') -> '_2318.Clutch':
        ''' 'AddClutch' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.Clutch
        '''

        name = str(name)
        method_result = self.wrapped.AddClutch(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_synchroniser(self, name: Optional['str'] = 'Synchroniser') -> '_2342.Synchroniser':
        ''' 'AddSynchroniser' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.Synchroniser
        '''

        name = str(name)
        method_result = self.wrapped.AddSynchroniser(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_rolling_ring(self, name: Optional['str'] = 'Rolling Ring') -> '_2336.RollingRing':
        ''' 'AddRollingRing' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.RollingRing
        '''

        name = str(name)
        method_result = self.wrapped.AddRollingRing(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_concept_coupling(self, name: Optional['str'] = 'Concept Coupling') -> '_2321.ConceptCoupling':
        ''' 'AddConceptCoupling' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.ConceptCoupling
        '''

        name = str(name)
        method_result = self.wrapped.AddConceptCoupling(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cvt(self, name: Optional['str'] = 'CVT') -> '_2326.CVT':
        ''' 'AddCVT' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.CVT
        '''

        name = str(name)
        method_result = self.wrapped.AddCVT(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_spring_damper(self, name: Optional['str'] = 'Spring Damper') -> '_2340.SpringDamper':
        ''' 'AddSpringDamper' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.SpringDamper
        '''

        name = str(name)
        method_result = self.wrapped.AddSpringDamper(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_torque_converter(self, name: Optional['str'] = 'Torque Converter') -> '_2347.TorqueConverter':
        ''' 'AddTorqueConverter' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.TorqueConverter
        '''

        name = str(name)
        method_result = self.wrapped.AddTorqueConverter(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_bolted_joint(self, name: Optional['str'] = 'Bolted Joint') -> '_2185.BoltedJoint':
        ''' 'AddBoltedJoint' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.BoltedJoint
        '''

        name = str(name)
        method_result = self.wrapped.AddBoltedJoint(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_belt_drive_with_options(self, belt_creation_options: Optional['_2311.BeltCreationOptions'] = None) -> '_2316.BeltDrive':
        ''' 'AddBeltDrive' is the original name of this method.

        Args:
            belt_creation_options (mastapy.system_model.part_model.creation_options.BeltCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.couplings.BeltDrive
        '''

        method_result = self.wrapped.AddBeltDrive.Overloads[_BELT_CREATION_OPTIONS](belt_creation_options.wrapped if belt_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_belt_drive(self, centre_distance: Optional['float'] = 0.1, pulley_a_diameter: Optional['float'] = 0.08, pulley_b_diameter: Optional['float'] = 0.08, name: Optional['str'] = 'Belt Drive') -> '_2316.BeltDrive':
        ''' 'AddBeltDrive' is the original name of this method.

        Args:
            centre_distance (float, optional)
            pulley_a_diameter (float, optional)
            pulley_b_diameter (float, optional)
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.couplings.BeltDrive
        '''

        centre_distance = float(centre_distance)
        pulley_a_diameter = float(pulley_a_diameter)
        pulley_b_diameter = float(pulley_b_diameter)
        name = str(name)
        method_result = self.wrapped.AddBeltDrive.Overloads[_DOUBLE, _DOUBLE, _DOUBLE, _STRING](centre_distance if centre_distance else 0.0, pulley_a_diameter if pulley_a_diameter else 0.0, pulley_b_diameter if pulley_b_diameter else 0.0, name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_planet_carrier_with_options(self, planet_carrier_creation_options: Optional['_2314.PlanetCarrierCreationOptions'] = None) -> '_2210.PlanetCarrier':
        ''' 'AddPlanetCarrier' is the original name of this method.

        Args:
            planet_carrier_creation_options (mastapy.system_model.part_model.creation_options.PlanetCarrierCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.PlanetCarrier
        '''

        method_result = self.wrapped.AddPlanetCarrier.Overloads[_PLANET_CARRIER_CREATION_OPTIONS](planet_carrier_creation_options.wrapped if planet_carrier_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_planet_carrier(self, number_of_planets: Optional['int'] = 3, diameter: Optional['float'] = 0.05) -> '_2210.PlanetCarrier':
        ''' 'AddPlanetCarrier' is the original name of this method.

        Args:
            number_of_planets (int, optional)
            diameter (float, optional)

        Returns:
            mastapy.system_model.part_model.PlanetCarrier
        '''

        number_of_planets = int(number_of_planets)
        diameter = float(diameter)
        method_result = self.wrapped.AddPlanetCarrier.Overloads[_INT_32, _DOUBLE](number_of_planets if number_of_planets else 0, diameter if diameter else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_shaft_with_options(self, shaft_creation_options: '_2315.ShaftCreationOptions') -> '_2223.Shaft':
        ''' 'AddShaft' is the original name of this method.

        Args:
            shaft_creation_options (mastapy.system_model.part_model.creation_options.ShaftCreationOptions)

        Returns:
            mastapy.system_model.part_model.shaft_model.Shaft
        '''

        method_result = self.wrapped.AddShaft.Overloads[_SHAFT_CREATION_OPTIONS](shaft_creation_options.wrapped if shaft_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_shaft(self, length: Optional['float'] = 0.1, outer_diameter: Optional['float'] = 0.025, bore: Optional['float'] = 0.0, name: Optional['str'] = 'Shaft') -> '_2223.Shaft':
        ''' 'AddShaft' is the original name of this method.

        Args:
            length (float, optional)
            outer_diameter (float, optional)
            bore (float, optional)
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.shaft_model.Shaft
        '''

        length = float(length)
        outer_diameter = float(outer_diameter)
        bore = float(bore)
        name = str(name)
        method_result = self.wrapped.AddShaft.Overloads[_DOUBLE, _DOUBLE, _DOUBLE, _STRING](length if length else 0.0, outer_diameter if outer_diameter else 0.0, bore if bore else 0.0, name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cylindrical_gear_pair_with_options(self, cylindrical_gear_pair_creation_options: Optional['_1093.CylindricalGearPairCreationOptions'] = None) -> '_2266.CylindricalGearSet':
        ''' 'AddCylindricalGearPair' is the original name of this method.

        Args:
            cylindrical_gear_pair_creation_options (mastapy.gears.gear_designs.creation_options.CylindricalGearPairCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        method_result = self.wrapped.AddCylindricalGearPair.Overloads[_CYLINDRICAL_GEAR_PAIR_CREATION_OPTIONS](cylindrical_gear_pair_creation_options.wrapped if cylindrical_gear_pair_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cylindrical_gear_pair(self, centre_distance: 'float') -> '_2266.CylindricalGearSet':
        ''' 'AddCylindricalGearPair' is the original name of this method.

        Args:
            centre_distance (float)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        centre_distance = float(centre_distance)
        method_result = self.wrapped.AddCylindricalGearPair.Overloads[_DOUBLE](centre_distance if centre_distance else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cylindrical_gear_set_with_options(self, cylindrical_gear_linear_train_creation_options: Optional['_2313.CylindricalGearLinearTrainCreationOptions'] = None) -> '_2266.CylindricalGearSet':
        ''' 'AddCylindricalGearSet' is the original name of this method.

        Args:
            cylindrical_gear_linear_train_creation_options (mastapy.system_model.part_model.creation_options.CylindricalGearLinearTrainCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        method_result = self.wrapped.AddCylindricalGearSet.Overloads[_CYLINDRICAL_GEAR_LINEAR_TRAIN_CREATION_OPTIONS](cylindrical_gear_linear_train_creation_options.wrapped if cylindrical_gear_linear_train_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cylindrical_gear_set(self, name: 'str', centre_distances: 'List[float]') -> '_2266.CylindricalGearSet':
        ''' 'AddCylindricalGearSet' is the original name of this method.

        Args:
            name (str)
            centre_distances (List[float])

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        name = str(name)
        centre_distances = conversion.mp_to_pn_array_float(centre_distances)
        method_result = self.wrapped.AddCylindricalGearSet.Overloads[_STRING, _ARRAY[_DOUBLE]](name if name else '', centre_distances)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cylindrical_gear_set_extended(self, name: 'str', normal_pressure_angle: 'float', helix_angle: 'float', normal_module: 'float', pinion_hand: '_299.Hand', centre_distances: 'List[float]') -> '_2266.CylindricalGearSet':
        ''' 'AddCylindricalGearSet' is the original name of this method.

        Args:
            name (str)
            normal_pressure_angle (float)
            helix_angle (float)
            normal_module (float)
            pinion_hand (mastapy.gears.Hand)
            centre_distances (List[float])

        Returns:
            mastapy.system_model.part_model.gears.CylindricalGearSet
        '''

        name = str(name)
        normal_pressure_angle = float(normal_pressure_angle)
        helix_angle = float(helix_angle)
        normal_module = float(normal_module)
        pinion_hand = conversion.mp_to_pn_enum(pinion_hand)
        centre_distances = conversion.mp_to_pn_array_float(centre_distances)
        method_result = self.wrapped.AddCylindricalGearSet.Overloads[_STRING, _DOUBLE, _DOUBLE, _DOUBLE, _HAND, _ARRAY[_DOUBLE]](name if name else '', normal_pressure_angle if normal_pressure_angle else 0.0, helix_angle if helix_angle else 0.0, normal_module if normal_module else 0.0, pinion_hand, centre_distances)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_spiral_bevel_gear_set_with_options(self, spiral_bevel_gear_set_creation_options: Optional['_1096.SpiralBevelGearSetCreationOptions'] = None) -> '_2284.SpiralBevelGearSet':
        ''' 'AddSpiralBevelGearSet' is the original name of this method.

        Args:
            spiral_bevel_gear_set_creation_options (mastapy.gears.gear_designs.creation_options.SpiralBevelGearSetCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.gears.SpiralBevelGearSet
        '''

        method_result = self.wrapped.AddSpiralBevelGearSet.Overloads[_SPIRAL_BEVEL_GEAR_SET_CREATION_OPTIONS](spiral_bevel_gear_set_creation_options.wrapped if spiral_bevel_gear_set_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_spiral_bevel_gear_set_detailed(self, name: Optional['str'] = 'Spiral Bevel Gear Set', outer_transverse_module: Optional['float'] = 0.00635, pressure_angle: Optional['float'] = 0.02, mean_spiral_angle: Optional['float'] = 0.523599, wheel_number_of_teeth: Optional['int'] = 43, pinion_number_of_teeth: Optional['int'] = 14, wheel_face_width: Optional['float'] = 0.02, pinion_face_width: Optional['float'] = 0.02, pinion_face_width_offset: Optional['float'] = 0.0, shaft_angle: Optional['float'] = 1.5708) -> '_2284.SpiralBevelGearSet':
        ''' 'AddSpiralBevelGearSet' is the original name of this method.

        Args:
            name (str, optional)
            outer_transverse_module (float, optional)
            pressure_angle (float, optional)
            mean_spiral_angle (float, optional)
            wheel_number_of_teeth (int, optional)
            pinion_number_of_teeth (int, optional)
            wheel_face_width (float, optional)
            pinion_face_width (float, optional)
            pinion_face_width_offset (float, optional)
            shaft_angle (float, optional)

        Returns:
            mastapy.system_model.part_model.gears.SpiralBevelGearSet
        '''

        name = str(name)
        outer_transverse_module = float(outer_transverse_module)
        pressure_angle = float(pressure_angle)
        mean_spiral_angle = float(mean_spiral_angle)
        wheel_number_of_teeth = int(wheel_number_of_teeth)
        pinion_number_of_teeth = int(pinion_number_of_teeth)
        wheel_face_width = float(wheel_face_width)
        pinion_face_width = float(pinion_face_width)
        pinion_face_width_offset = float(pinion_face_width_offset)
        shaft_angle = float(shaft_angle)
        method_result = self.wrapped.AddSpiralBevelGearSet.Overloads[_STRING, _DOUBLE, _DOUBLE, _DOUBLE, _INT_32, _INT_32, _DOUBLE, _DOUBLE, _DOUBLE, _DOUBLE](name if name else '', outer_transverse_module if outer_transverse_module else 0.0, pressure_angle if pressure_angle else 0.0, mean_spiral_angle if mean_spiral_angle else 0.0, wheel_number_of_teeth if wheel_number_of_teeth else 0, pinion_number_of_teeth if pinion_number_of_teeth else 0, wheel_face_width if wheel_face_width else 0.0, pinion_face_width if pinion_face_width else 0.0, pinion_face_width_offset if pinion_face_width_offset else 0.0, shaft_angle if shaft_angle else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_hypoid_gear_set_detailed(self, name: Optional['str'] = 'Hypoid Gear Set', pinion_number_of_teeth: Optional['int'] = 7, wheel_number_of_teeth: Optional['int'] = 41, outer_transverse_module: Optional['float'] = 0.0109756, wheel_face_width: Optional['float'] = 0.072, offset: Optional['float'] = 0.045, average_pressure_angle: Optional['float'] = 0.3926991, design_method: Optional['_1126.AGMAGleasonConicalGearGeometryMethods'] = _1126.AGMAGleasonConicalGearGeometryMethods.GLEASON) -> '_2275.HypoidGearSet':
        ''' 'AddHypoidGearSet' is the original name of this method.

        Args:
            name (str, optional)
            pinion_number_of_teeth (int, optional)
            wheel_number_of_teeth (int, optional)
            outer_transverse_module (float, optional)
            wheel_face_width (float, optional)
            offset (float, optional)
            average_pressure_angle (float, optional)
            design_method (mastapy.gears.gear_designs.bevel.AGMAGleasonConicalGearGeometryMethods, optional)

        Returns:
            mastapy.system_model.part_model.gears.HypoidGearSet
        '''

        name = str(name)
        pinion_number_of_teeth = int(pinion_number_of_teeth)
        wheel_number_of_teeth = int(wheel_number_of_teeth)
        outer_transverse_module = float(outer_transverse_module)
        wheel_face_width = float(wheel_face_width)
        offset = float(offset)
        average_pressure_angle = float(average_pressure_angle)
        design_method = conversion.mp_to_pn_enum(design_method)
        method_result = self.wrapped.AddHypoidGearSet.Overloads[_STRING, _INT_32, _INT_32, _DOUBLE, _DOUBLE, _DOUBLE, _DOUBLE, _AGMA_GLEASON_CONICAL_GEAR_GEOMETRY_METHODS](name if name else '', pinion_number_of_teeth if pinion_number_of_teeth else 0, wheel_number_of_teeth if wheel_number_of_teeth else 0, outer_transverse_module if outer_transverse_module else 0.0, wheel_face_width if wheel_face_width else 0.0, offset if offset else 0.0, average_pressure_angle if average_pressure_angle else 0.0, design_method)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_bearing(self, name: 'str') -> '_2182.Bearing':
        ''' 'AddBearing' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        method_result = self.wrapped.AddBearing.Overloads[_STRING](name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cycloidal_assembly_with_options(self, cycloidal_assembly_creation_options: Optional['_2312.CycloidalAssemblyCreationOptions'] = None) -> '_2308.CycloidalAssembly':
        ''' 'AddCycloidalAssembly' is the original name of this method.

        Args:
            cycloidal_assembly_creation_options (mastapy.system_model.part_model.creation_options.CycloidalAssemblyCreationOptions, optional)

        Returns:
            mastapy.system_model.part_model.cycloidal.CycloidalAssembly
        '''

        method_result = self.wrapped.AddCycloidalAssembly.Overloads[_CYCLOIDAL_ASSEMBLY_CREATION_OPTIONS](cycloidal_assembly_creation_options.wrapped if cycloidal_assembly_creation_options else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_cycloidal_assembly(self, number_of_discs: Optional['int'] = 1, number_of_pins: Optional['int'] = 10, name: Optional['str'] = 'Cycloidal Assembly') -> '_2308.CycloidalAssembly':
        ''' 'AddCycloidalAssembly' is the original name of this method.

        Args:
            number_of_discs (int, optional)
            number_of_pins (int, optional)
            name (str, optional)

        Returns:
            mastapy.system_model.part_model.cycloidal.CycloidalAssembly
        '''

        number_of_discs = int(number_of_discs)
        number_of_pins = int(number_of_pins)
        name = str(name)
        method_result = self.wrapped.AddCycloidalAssembly.Overloads[_INT_32, _INT_32, _STRING](number_of_discs if number_of_discs else 0, number_of_pins if number_of_pins else 0, name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_axial_clearance_bearing(self, name: 'str', contact_diameter: 'float') -> '_2182.Bearing':
        ''' 'AddAxialClearanceBearing' is the original name of this method.

        Args:
            name (str)
            contact_diameter (float)

        Returns:
            mastapy.system_model.part_model.Bearing
        '''

        name = str(name)
        contact_diameter = float(contact_diameter)
        method_result = self.wrapped.AddAxialClearanceBearing(name if name else '', contact_diameter if contact_diameter else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_shaft_hub_connection(self, name: 'str') -> '_2338.ShaftHubConnection':
        ''' 'AddShaftHubConnection' is the original name of this method.

        Args:
            name (str)

        Returns:
            mastapy.system_model.part_model.couplings.ShaftHubConnection
        '''

        name = str(name)
        method_result = self.wrapped.AddShaftHubConnection(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
