'''_1613.py

MASTAGUI
'''


from typing import List, Dict

from mastapy._internal import constructor, conversion, enum_with_selected_value_runtime
from mastapy.system_model import _1951, _1947
from mastapy.system_model.connections_and_sockets import (
    _2007, _2010, _2011, _2014,
    _2015, _2023, _2029, _2034,
    _2037
)
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.connections_and_sockets.gears import (
    _2041, _2043, _2045, _2047,
    _2049, _2051, _2053, _2055,
    _2057, _2060, _2061, _2062,
    _2065, _2067, _2069, _2071,
    _2073
)
from mastapy.system_model.connections_and_sockets.cycloidal import _2077, _2080, _2083
from mastapy.system_model.connections_and_sockets.couplings import (
    _2084, _2086, _2088, _2090,
    _2092, _2094
)
from mastapy.system_model.part_model import (
    _2176, _2177, _2178, _2179,
    _2182, _2184, _2185, _2186,
    _2189, _2190, _2193, _2194,
    _2195, _2196, _2203, _2204,
    _2205, _2207, _2209, _2210,
    _2212, _2213, _2215, _2217,
    _2218, _2220
)
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
from mastapy._math.color import Color
from mastapy._math.vector_3d import Vector3D
from mastapy.utility.operation_modes import _1561
from mastapy.math_utility import _1291, _1310
from mastapy.nodal_analysis.geometry_modeller_link import _150
from mastapy._internal.python_net import python_net_import
from mastapy import _0

_FACETED_BODY = python_net_import('SMT.MastaAPI.MathUtility', 'FacetedBody')
_STRING = python_net_import('System', 'String')
_MASTAGUI = python_net_import('SMT.MastaAPI.SystemModelGUI', 'MASTAGUI')


__docformat__ = 'restructuredtext en'
__all__ = ('MASTAGUI',)


class MASTAGUI(_0.APIBase):
    '''MASTAGUI

    This is a mastapy class.
    '''

    TYPE = _MASTAGUI

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MASTAGUI.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_paused(self) -> 'bool':
        '''bool: 'IsPaused' is the original name of this property.'''

        return self.wrapped.IsPaused

    @is_paused.setter
    def is_paused(self, value: 'bool'):
        self.wrapped.IsPaused = bool(value) if value else False

    @property
    def is_initialised(self) -> 'bool':
        '''bool: 'IsInitialised' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsInitialised

    @property
    def is_remoting(self) -> 'bool':
        '''bool: 'IsRemoting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsRemoting

    @property
    def selected_design_entity(self) -> '_1951.DesignEntity':
        '''DesignEntity: 'SelectedDesignEntity' is the original name of this property.'''

        if _1951.DesignEntity.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to DesignEntity. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity.setter
    def selected_design_entity(self, value: '_1951.DesignEntity'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_abstract_shaft_to_mountable_component_connection(self) -> '_2007.AbstractShaftToMountableComponentConnection':
        '''AbstractShaftToMountableComponentConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2007.AbstractShaftToMountableComponentConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AbstractShaftToMountableComponentConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_abstract_shaft_to_mountable_component_connection.setter
    def selected_design_entity_of_type_abstract_shaft_to_mountable_component_connection(self, value: '_2007.AbstractShaftToMountableComponentConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_belt_connection(self) -> '_2010.BeltConnection':
        '''BeltConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2010.BeltConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BeltConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_belt_connection.setter
    def selected_design_entity_of_type_belt_connection(self, value: '_2010.BeltConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_coaxial_connection(self) -> '_2011.CoaxialConnection':
        '''CoaxialConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2011.CoaxialConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CoaxialConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_coaxial_connection.setter
    def selected_design_entity_of_type_coaxial_connection(self, value: '_2011.CoaxialConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_connection(self) -> '_2014.Connection':
        '''Connection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2014.Connection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Connection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_connection.setter
    def selected_design_entity_of_type_connection(self, value: '_2014.Connection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cvt_belt_connection(self) -> '_2015.CVTBeltConnection':
        '''CVTBeltConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2015.CVTBeltConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CVTBeltConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cvt_belt_connection.setter
    def selected_design_entity_of_type_cvt_belt_connection(self, value: '_2015.CVTBeltConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_inter_mountable_component_connection(self) -> '_2023.InterMountableComponentConnection':
        '''InterMountableComponentConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2023.InterMountableComponentConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to InterMountableComponentConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_inter_mountable_component_connection.setter
    def selected_design_entity_of_type_inter_mountable_component_connection(self, value: '_2023.InterMountableComponentConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_planetary_connection(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2029.PlanetaryConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PlanetaryConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_planetary_connection.setter
    def selected_design_entity_of_type_planetary_connection(self, value: '_2029.PlanetaryConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_rolling_ring_connection(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2034.RollingRingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RollingRingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_rolling_ring_connection.setter
    def selected_design_entity_of_type_rolling_ring_connection(self, value: '_2034.RollingRingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_shaft_to_mountable_component_connection(self) -> '_2037.ShaftToMountableComponentConnection':
        '''ShaftToMountableComponentConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2037.ShaftToMountableComponentConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ShaftToMountableComponentConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_shaft_to_mountable_component_connection.setter
    def selected_design_entity_of_type_shaft_to_mountable_component_connection(self, value: '_2037.ShaftToMountableComponentConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_agma_gleason_conical_gear_mesh(self) -> '_2041.AGMAGleasonConicalGearMesh':
        '''AGMAGleasonConicalGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2041.AGMAGleasonConicalGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AGMAGleasonConicalGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_agma_gleason_conical_gear_mesh.setter
    def selected_design_entity_of_type_agma_gleason_conical_gear_mesh(self, value: '_2041.AGMAGleasonConicalGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_differential_gear_mesh(self) -> '_2043.BevelDifferentialGearMesh':
        '''BevelDifferentialGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2043.BevelDifferentialGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelDifferentialGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_differential_gear_mesh.setter
    def selected_design_entity_of_type_bevel_differential_gear_mesh(self, value: '_2043.BevelDifferentialGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_gear_mesh(self) -> '_2045.BevelGearMesh':
        '''BevelGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2045.BevelGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_gear_mesh.setter
    def selected_design_entity_of_type_bevel_gear_mesh(self, value: '_2045.BevelGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_gear_mesh(self) -> '_2047.ConceptGearMesh':
        '''ConceptGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2047.ConceptGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_gear_mesh.setter
    def selected_design_entity_of_type_concept_gear_mesh(self, value: '_2047.ConceptGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_conical_gear_mesh(self) -> '_2049.ConicalGearMesh':
        '''ConicalGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2049.ConicalGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConicalGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_conical_gear_mesh.setter
    def selected_design_entity_of_type_conical_gear_mesh(self, value: '_2049.ConicalGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cylindrical_gear_mesh(self) -> '_2051.CylindricalGearMesh':
        '''CylindricalGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2051.CylindricalGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CylindricalGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cylindrical_gear_mesh.setter
    def selected_design_entity_of_type_cylindrical_gear_mesh(self, value: '_2051.CylindricalGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_face_gear_mesh(self) -> '_2053.FaceGearMesh':
        '''FaceGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2053.FaceGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to FaceGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_face_gear_mesh.setter
    def selected_design_entity_of_type_face_gear_mesh(self, value: '_2053.FaceGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_gear_mesh(self) -> '_2055.GearMesh':
        '''GearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2055.GearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to GearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_gear_mesh.setter
    def selected_design_entity_of_type_gear_mesh(self, value: '_2055.GearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_hypoid_gear_mesh(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2057.HypoidGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to HypoidGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_hypoid_gear_mesh.setter
    def selected_design_entity_of_type_hypoid_gear_mesh(self, value: '_2057.HypoidGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh(self) -> '_2060.KlingelnbergCycloPalloidConicalGearMesh':
        '''KlingelnbergCycloPalloidConicalGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2060.KlingelnbergCycloPalloidConicalGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidConicalGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh(self, value: '_2060.KlingelnbergCycloPalloidConicalGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh(self) -> '_2061.KlingelnbergCycloPalloidHypoidGearMesh':
        '''KlingelnbergCycloPalloidHypoidGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2061.KlingelnbergCycloPalloidHypoidGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidHypoidGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh(self, value: '_2061.KlingelnbergCycloPalloidHypoidGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(self) -> '_2062.KlingelnbergCycloPalloidSpiralBevelGearMesh':
        '''KlingelnbergCycloPalloidSpiralBevelGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2062.KlingelnbergCycloPalloidSpiralBevelGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidSpiralBevelGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(self, value: '_2062.KlingelnbergCycloPalloidSpiralBevelGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spiral_bevel_gear_mesh(self) -> '_2065.SpiralBevelGearMesh':
        '''SpiralBevelGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2065.SpiralBevelGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpiralBevelGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spiral_bevel_gear_mesh.setter
    def selected_design_entity_of_type_spiral_bevel_gear_mesh(self, value: '_2065.SpiralBevelGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_diff_gear_mesh(self) -> '_2067.StraightBevelDiffGearMesh':
        '''StraightBevelDiffGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2067.StraightBevelDiffGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelDiffGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_diff_gear_mesh.setter
    def selected_design_entity_of_type_straight_bevel_diff_gear_mesh(self, value: '_2067.StraightBevelDiffGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_gear_mesh(self) -> '_2069.StraightBevelGearMesh':
        '''StraightBevelGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2069.StraightBevelGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_gear_mesh.setter
    def selected_design_entity_of_type_straight_bevel_gear_mesh(self, value: '_2069.StraightBevelGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_worm_gear_mesh(self) -> '_2071.WormGearMesh':
        '''WormGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2071.WormGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to WormGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_worm_gear_mesh.setter
    def selected_design_entity_of_type_worm_gear_mesh(self, value: '_2071.WormGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_zerol_bevel_gear_mesh(self) -> '_2073.ZerolBevelGearMesh':
        '''ZerolBevelGearMesh: 'SelectedDesignEntity' is the original name of this property.'''

        if _2073.ZerolBevelGearMesh.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ZerolBevelGearMesh. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_zerol_bevel_gear_mesh.setter
    def selected_design_entity_of_type_zerol_bevel_gear_mesh(self, value: '_2073.ZerolBevelGearMesh'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cycloidal_disc_central_bearing_connection(self) -> '_2077.CycloidalDiscCentralBearingConnection':
        '''CycloidalDiscCentralBearingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2077.CycloidalDiscCentralBearingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CycloidalDiscCentralBearingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cycloidal_disc_central_bearing_connection.setter
    def selected_design_entity_of_type_cycloidal_disc_central_bearing_connection(self, value: '_2077.CycloidalDiscCentralBearingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cycloidal_disc_planetary_bearing_connection(self) -> '_2080.CycloidalDiscPlanetaryBearingConnection':
        '''CycloidalDiscPlanetaryBearingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2080.CycloidalDiscPlanetaryBearingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CycloidalDiscPlanetaryBearingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cycloidal_disc_planetary_bearing_connection.setter
    def selected_design_entity_of_type_cycloidal_disc_planetary_bearing_connection(self, value: '_2080.CycloidalDiscPlanetaryBearingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_ring_pins_to_disc_connection(self) -> '_2083.RingPinsToDiscConnection':
        '''RingPinsToDiscConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2083.RingPinsToDiscConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RingPinsToDiscConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_ring_pins_to_disc_connection.setter
    def selected_design_entity_of_type_ring_pins_to_disc_connection(self, value: '_2083.RingPinsToDiscConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_clutch_connection(self) -> '_2084.ClutchConnection':
        '''ClutchConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2084.ClutchConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ClutchConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_clutch_connection.setter
    def selected_design_entity_of_type_clutch_connection(self, value: '_2084.ClutchConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_coupling_connection(self) -> '_2086.ConceptCouplingConnection':
        '''ConceptCouplingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2086.ConceptCouplingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptCouplingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_coupling_connection.setter
    def selected_design_entity_of_type_concept_coupling_connection(self, value: '_2086.ConceptCouplingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_coupling_connection(self) -> '_2088.CouplingConnection':
        '''CouplingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2088.CouplingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CouplingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_coupling_connection.setter
    def selected_design_entity_of_type_coupling_connection(self, value: '_2088.CouplingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_part_to_part_shear_coupling_connection(self) -> '_2090.PartToPartShearCouplingConnection':
        '''PartToPartShearCouplingConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2090.PartToPartShearCouplingConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PartToPartShearCouplingConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_part_to_part_shear_coupling_connection.setter
    def selected_design_entity_of_type_part_to_part_shear_coupling_connection(self, value: '_2090.PartToPartShearCouplingConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spring_damper_connection(self) -> '_2092.SpringDamperConnection':
        '''SpringDamperConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2092.SpringDamperConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpringDamperConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spring_damper_connection.setter
    def selected_design_entity_of_type_spring_damper_connection(self, value: '_2092.SpringDamperConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_torque_converter_connection(self) -> '_2094.TorqueConverterConnection':
        '''TorqueConverterConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2094.TorqueConverterConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to TorqueConverterConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_torque_converter_connection.setter
    def selected_design_entity_of_type_torque_converter_connection(self, value: '_2094.TorqueConverterConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_assembly(self) -> '_2176.Assembly':
        '''Assembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2176.Assembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Assembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_assembly.setter
    def selected_design_entity_of_type_assembly(self, value: '_2176.Assembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_abstract_assembly(self) -> '_2177.AbstractAssembly':
        '''AbstractAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2177.AbstractAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AbstractAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_abstract_assembly.setter
    def selected_design_entity_of_type_abstract_assembly(self, value: '_2177.AbstractAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'SelectedDesignEntity' is the original name of this property.'''

        if _2178.AbstractShaft.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AbstractShaft. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_abstract_shaft.setter
    def selected_design_entity_of_type_abstract_shaft(self, value: '_2178.AbstractShaft'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'SelectedDesignEntity' is the original name of this property.'''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_abstract_shaft_or_housing.setter
    def selected_design_entity_of_type_abstract_shaft_or_housing(self, value: '_2179.AbstractShaftOrHousing'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'SelectedDesignEntity' is the original name of this property.'''

        if _2182.Bearing.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Bearing. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bearing.setter
    def selected_design_entity_of_type_bearing(self, value: '_2182.Bearing'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'SelectedDesignEntity' is the original name of this property.'''

        if _2184.Bolt.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Bolt. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bolt.setter
    def selected_design_entity_of_type_bolt(self, value: '_2184.Bolt'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bolted_joint(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'SelectedDesignEntity' is the original name of this property.'''

        if _2185.BoltedJoint.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BoltedJoint. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bolted_joint.setter
    def selected_design_entity_of_type_bolted_joint(self, value: '_2185.BoltedJoint'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_component(self) -> '_2186.Component':
        '''Component: 'SelectedDesignEntity' is the original name of this property.'''

        if _2186.Component.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Component. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_component.setter
    def selected_design_entity_of_type_component(self, value: '_2186.Component'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'SelectedDesignEntity' is the original name of this property.'''

        if _2189.Connector.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Connector. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_connector.setter
    def selected_design_entity_of_type_connector(self, value: '_2189.Connector'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'SelectedDesignEntity' is the original name of this property.'''

        if _2190.Datum.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Datum. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_datum.setter
    def selected_design_entity_of_type_datum(self, value: '_2190.Datum'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'SelectedDesignEntity' is the original name of this property.'''

        if _2193.ExternalCADModel.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ExternalCADModel. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_external_cad_model.setter
    def selected_design_entity_of_type_external_cad_model(self, value: '_2193.ExternalCADModel'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'SelectedDesignEntity' is the original name of this property.'''

        if _2194.FEPart.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to FEPart. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_fe_part.setter
    def selected_design_entity_of_type_fe_part(self, value: '_2194.FEPart'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_flexible_pin_assembly(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2195.FlexiblePinAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to FlexiblePinAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_flexible_pin_assembly.setter
    def selected_design_entity_of_type_flexible_pin_assembly(self, value: '_2195.FlexiblePinAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'SelectedDesignEntity' is the original name of this property.'''

        if _2196.GuideDxfModel.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to GuideDxfModel. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_guide_dxf_model.setter
    def selected_design_entity_of_type_guide_dxf_model(self, value: '_2196.GuideDxfModel'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'SelectedDesignEntity' is the original name of this property.'''

        if _2203.MassDisc.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to MassDisc. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_mass_disc.setter
    def selected_design_entity_of_type_mass_disc(self, value: '_2203.MassDisc'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'SelectedDesignEntity' is the original name of this property.'''

        if _2204.MeasurementComponent.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to MeasurementComponent. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_measurement_component.setter
    def selected_design_entity_of_type_measurement_component(self, value: '_2204.MeasurementComponent'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'SelectedDesignEntity' is the original name of this property.'''

        if _2205.MountableComponent.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to MountableComponent. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_mountable_component.setter
    def selected_design_entity_of_type_mountable_component(self, value: '_2205.MountableComponent'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'SelectedDesignEntity' is the original name of this property.'''

        if _2207.OilSeal.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to OilSeal. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_oil_seal.setter
    def selected_design_entity_of_type_oil_seal(self, value: '_2207.OilSeal'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_part(self) -> '_2209.Part':
        '''Part: 'SelectedDesignEntity' is the original name of this property.'''

        if _2209.Part.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Part. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_part.setter
    def selected_design_entity_of_type_part(self, value: '_2209.Part'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'SelectedDesignEntity' is the original name of this property.'''

        if _2210.PlanetCarrier.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PlanetCarrier. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_planet_carrier.setter
    def selected_design_entity_of_type_planet_carrier(self, value: '_2210.PlanetCarrier'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'SelectedDesignEntity' is the original name of this property.'''

        if _2212.PointLoad.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PointLoad. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_point_load.setter
    def selected_design_entity_of_type_point_load(self, value: '_2212.PointLoad'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'SelectedDesignEntity' is the original name of this property.'''

        if _2213.PowerLoad.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PowerLoad. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_power_load.setter
    def selected_design_entity_of_type_power_load(self, value: '_2213.PowerLoad'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_root_assembly(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2215.RootAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RootAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_root_assembly.setter
    def selected_design_entity_of_type_root_assembly(self, value: '_2215.RootAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_specialised_assembly(self) -> '_2217.SpecialisedAssembly':
        '''SpecialisedAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2217.SpecialisedAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpecialisedAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_specialised_assembly.setter
    def selected_design_entity_of_type_specialised_assembly(self, value: '_2217.SpecialisedAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'SelectedDesignEntity' is the original name of this property.'''

        if _2218.UnbalancedMass.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to UnbalancedMass. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_unbalanced_mass.setter
    def selected_design_entity_of_type_unbalanced_mass(self, value: '_2218.UnbalancedMass'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'SelectedDesignEntity' is the original name of this property.'''

        if _2220.VirtualComponent.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to VirtualComponent. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_virtual_component.setter
    def selected_design_entity_of_type_virtual_component(self, value: '_2220.VirtualComponent'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'SelectedDesignEntity' is the original name of this property.'''

        if _2223.Shaft.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Shaft. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_shaft.setter
    def selected_design_entity_of_type_shaft(self, value: '_2223.Shaft'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AGMAGleasonConicalGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_agma_gleason_conical_gear.setter
    def selected_design_entity_of_type_agma_gleason_conical_gear(self, value: '_2253.AGMAGleasonConicalGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_agma_gleason_conical_gear_set(self) -> '_2254.AGMAGleasonConicalGearSet':
        '''AGMAGleasonConicalGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2254.AGMAGleasonConicalGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to AGMAGleasonConicalGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_agma_gleason_conical_gear_set.setter
    def selected_design_entity_of_type_agma_gleason_conical_gear_set(self, value: '_2254.AGMAGleasonConicalGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_differential_gear.setter
    def selected_design_entity_of_type_bevel_differential_gear(self, value: '_2255.BevelDifferentialGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_differential_gear_set(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2256.BevelDifferentialGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelDifferentialGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_differential_gear_set.setter
    def selected_design_entity_of_type_bevel_differential_gear_set(self, value: '_2256.BevelDifferentialGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelDifferentialPlanetGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_differential_planet_gear.setter
    def selected_design_entity_of_type_bevel_differential_planet_gear(self, value: '_2257.BevelDifferentialPlanetGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2258.BevelDifferentialSunGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelDifferentialSunGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_differential_sun_gear.setter
    def selected_design_entity_of_type_bevel_differential_sun_gear(self, value: '_2258.BevelDifferentialSunGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2259.BevelGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_gear.setter
    def selected_design_entity_of_type_bevel_gear(self, value: '_2259.BevelGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_bevel_gear_set(self) -> '_2260.BevelGearSet':
        '''BevelGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2260.BevelGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BevelGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_bevel_gear_set.setter
    def selected_design_entity_of_type_bevel_gear_set(self, value: '_2260.BevelGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2261.ConceptGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_gear.setter
    def selected_design_entity_of_type_concept_gear(self, value: '_2261.ConceptGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_gear_set(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2262.ConceptGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_gear_set.setter
    def selected_design_entity_of_type_concept_gear_set(self, value: '_2262.ConceptGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2263.ConicalGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConicalGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_conical_gear.setter
    def selected_design_entity_of_type_conical_gear(self, value: '_2263.ConicalGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_conical_gear_set(self) -> '_2264.ConicalGearSet':
        '''ConicalGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2264.ConicalGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConicalGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_conical_gear_set.setter
    def selected_design_entity_of_type_conical_gear_set(self, value: '_2264.ConicalGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2265.CylindricalGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CylindricalGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cylindrical_gear.setter
    def selected_design_entity_of_type_cylindrical_gear(self, value: '_2265.CylindricalGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cylindrical_gear_set(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CylindricalGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cylindrical_gear_set.setter
    def selected_design_entity_of_type_cylindrical_gear_set(self, value: '_2266.CylindricalGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2267.CylindricalPlanetGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CylindricalPlanetGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cylindrical_planet_gear.setter
    def selected_design_entity_of_type_cylindrical_planet_gear(self, value: '_2267.CylindricalPlanetGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2268.FaceGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to FaceGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_face_gear.setter
    def selected_design_entity_of_type_face_gear(self, value: '_2268.FaceGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_face_gear_set(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2269.FaceGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to FaceGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_face_gear_set.setter
    def selected_design_entity_of_type_face_gear_set(self, value: '_2269.FaceGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2270.Gear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Gear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_gear.setter
    def selected_design_entity_of_type_gear(self, value: '_2270.Gear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_gear_set(self) -> '_2272.GearSet':
        '''GearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2272.GearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to GearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_gear_set.setter
    def selected_design_entity_of_type_gear_set(self, value: '_2272.GearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2274.HypoidGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to HypoidGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_hypoid_gear.setter
    def selected_design_entity_of_type_hypoid_gear(self, value: '_2274.HypoidGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_hypoid_gear_set(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2275.HypoidGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to HypoidGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_hypoid_gear_set.setter
    def selected_design_entity_of_type_hypoid_gear_set(self, value: '_2275.HypoidGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear(self, value: '_2276.KlingelnbergCycloPalloidConicalGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        '''KlingelnbergCycloPalloidConicalGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2277.KlingelnbergCycloPalloidConicalGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidConicalGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_set.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self, value: '_2277.KlingelnbergCycloPalloidConicalGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self, value: '_2278.KlingelnbergCycloPalloidHypoidGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidHypoidGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self, value: '_2279.KlingelnbergCycloPalloidHypoidGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self, value: '_2280.KlingelnbergCycloPalloidSpiralBevelGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to KlingelnbergCycloPalloidSpiralBevelGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set.setter
    def selected_design_entity_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self, value: '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_planetary_gear_set(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2282.PlanetaryGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PlanetaryGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_planetary_gear_set.setter
    def selected_design_entity_of_type_planetary_gear_set(self, value: '_2282.PlanetaryGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2283.SpiralBevelGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpiralBevelGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spiral_bevel_gear.setter
    def selected_design_entity_of_type_spiral_bevel_gear(self, value: '_2283.SpiralBevelGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spiral_bevel_gear_set(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2284.SpiralBevelGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpiralBevelGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spiral_bevel_gear_set.setter
    def selected_design_entity_of_type_spiral_bevel_gear_set(self, value: '_2284.SpiralBevelGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2285.StraightBevelDiffGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelDiffGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_diff_gear.setter
    def selected_design_entity_of_type_straight_bevel_diff_gear(self, value: '_2285.StraightBevelDiffGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_diff_gear_set(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2286.StraightBevelDiffGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelDiffGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_diff_gear_set.setter
    def selected_design_entity_of_type_straight_bevel_diff_gear_set(self, value: '_2286.StraightBevelDiffGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2287.StraightBevelGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_gear.setter
    def selected_design_entity_of_type_straight_bevel_gear(self, value: '_2287.StraightBevelGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_gear_set(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2288.StraightBevelGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_gear_set.setter
    def selected_design_entity_of_type_straight_bevel_gear_set(self, value: '_2288.StraightBevelGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2289.StraightBevelPlanetGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelPlanetGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_planet_gear.setter
    def selected_design_entity_of_type_straight_bevel_planet_gear(self, value: '_2289.StraightBevelPlanetGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2290.StraightBevelSunGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to StraightBevelSunGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_straight_bevel_sun_gear.setter
    def selected_design_entity_of_type_straight_bevel_sun_gear(self, value: '_2290.StraightBevelSunGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2291.WormGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to WormGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_worm_gear.setter
    def selected_design_entity_of_type_worm_gear(self, value: '_2291.WormGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_worm_gear_set(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2292.WormGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to WormGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_worm_gear_set.setter
    def selected_design_entity_of_type_worm_gear_set(self, value: '_2292.WormGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'SelectedDesignEntity' is the original name of this property.'''

        if _2293.ZerolBevelGear.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ZerolBevelGear. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_zerol_bevel_gear.setter
    def selected_design_entity_of_type_zerol_bevel_gear(self, value: '_2293.ZerolBevelGear'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_zerol_bevel_gear_set(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'SelectedDesignEntity' is the original name of this property.'''

        if _2294.ZerolBevelGearSet.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ZerolBevelGearSet. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_zerol_bevel_gear_set.setter
    def selected_design_entity_of_type_zerol_bevel_gear_set(self, value: '_2294.ZerolBevelGearSet'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cycloidal_assembly(self) -> '_2308.CycloidalAssembly':
        '''CycloidalAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2308.CycloidalAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CycloidalAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cycloidal_assembly.setter
    def selected_design_entity_of_type_cycloidal_assembly(self, value: '_2308.CycloidalAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'SelectedDesignEntity' is the original name of this property.'''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CycloidalDisc. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cycloidal_disc.setter
    def selected_design_entity_of_type_cycloidal_disc(self, value: '_2309.CycloidalDisc'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'SelectedDesignEntity' is the original name of this property.'''

        if _2310.RingPins.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RingPins. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_ring_pins.setter
    def selected_design_entity_of_type_ring_pins(self, value: '_2310.RingPins'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_belt_drive(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'SelectedDesignEntity' is the original name of this property.'''

        if _2316.BeltDrive.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to BeltDrive. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_belt_drive.setter
    def selected_design_entity_of_type_belt_drive(self, value: '_2316.BeltDrive'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_clutch(self) -> '_2318.Clutch':
        '''Clutch: 'SelectedDesignEntity' is the original name of this property.'''

        if _2318.Clutch.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Clutch. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_clutch.setter
    def selected_design_entity_of_type_clutch(self, value: '_2318.Clutch'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2319.ClutchHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ClutchHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_clutch_half.setter
    def selected_design_entity_of_type_clutch_half(self, value: '_2319.ClutchHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_coupling(self) -> '_2321.ConceptCoupling':
        '''ConceptCoupling: 'SelectedDesignEntity' is the original name of this property.'''

        if _2321.ConceptCoupling.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptCoupling. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_coupling.setter
    def selected_design_entity_of_type_concept_coupling(self, value: '_2321.ConceptCoupling'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2322.ConceptCouplingHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ConceptCouplingHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_concept_coupling_half.setter
    def selected_design_entity_of_type_concept_coupling_half(self, value: '_2322.ConceptCouplingHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_coupling(self) -> '_2323.Coupling':
        '''Coupling: 'SelectedDesignEntity' is the original name of this property.'''

        if _2323.Coupling.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Coupling. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_coupling.setter
    def selected_design_entity_of_type_coupling(self, value: '_2323.Coupling'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2324.CouplingHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CouplingHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_coupling_half.setter
    def selected_design_entity_of_type_coupling_half(self, value: '_2324.CouplingHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cvt(self) -> '_2326.CVT':
        '''CVT: 'SelectedDesignEntity' is the original name of this property.'''

        if _2326.CVT.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CVT. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cvt.setter
    def selected_design_entity_of_type_cvt(self, value: '_2326.CVT'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'SelectedDesignEntity' is the original name of this property.'''

        if _2327.CVTPulley.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to CVTPulley. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_cvt_pulley.setter
    def selected_design_entity_of_type_cvt_pulley(self, value: '_2327.CVTPulley'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_part_to_part_shear_coupling(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'SelectedDesignEntity' is the original name of this property.'''

        if _2328.PartToPartShearCoupling.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PartToPartShearCoupling. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_part_to_part_shear_coupling.setter
    def selected_design_entity_of_type_part_to_part_shear_coupling(self, value: '_2328.PartToPartShearCoupling'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to PartToPartShearCouplingHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_part_to_part_shear_coupling_half.setter
    def selected_design_entity_of_type_part_to_part_shear_coupling_half(self, value: '_2329.PartToPartShearCouplingHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'SelectedDesignEntity' is the original name of this property.'''

        if _2330.Pulley.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Pulley. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_pulley.setter
    def selected_design_entity_of_type_pulley(self, value: '_2330.Pulley'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'SelectedDesignEntity' is the original name of this property.'''

        if _2336.RollingRing.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RollingRing. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_rolling_ring.setter
    def selected_design_entity_of_type_rolling_ring(self, value: '_2336.RollingRing'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_rolling_ring_assembly(self) -> '_2337.RollingRingAssembly':
        '''RollingRingAssembly: 'SelectedDesignEntity' is the original name of this property.'''

        if _2337.RollingRingAssembly.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to RollingRingAssembly. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_rolling_ring_assembly.setter
    def selected_design_entity_of_type_rolling_ring_assembly(self, value: '_2337.RollingRingAssembly'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'SelectedDesignEntity' is the original name of this property.'''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to ShaftHubConnection. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_shaft_hub_connection.setter
    def selected_design_entity_of_type_shaft_hub_connection(self, value: '_2338.ShaftHubConnection'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spring_damper(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'SelectedDesignEntity' is the original name of this property.'''

        if _2340.SpringDamper.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpringDamper. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spring_damper.setter
    def selected_design_entity_of_type_spring_damper(self, value: '_2340.SpringDamper'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2341.SpringDamperHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SpringDamperHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_spring_damper_half.setter
    def selected_design_entity_of_type_spring_damper_half(self, value: '_2341.SpringDamperHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_synchroniser(self) -> '_2342.Synchroniser':
        '''Synchroniser: 'SelectedDesignEntity' is the original name of this property.'''

        if _2342.Synchroniser.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to Synchroniser. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_synchroniser.setter
    def selected_design_entity_of_type_synchroniser(self, value: '_2342.Synchroniser'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'SelectedDesignEntity' is the original name of this property.'''

        if _2344.SynchroniserHalf.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SynchroniserHalf. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_synchroniser_half.setter
    def selected_design_entity_of_type_synchroniser_half(self, value: '_2344.SynchroniserHalf'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'SelectedDesignEntity' is the original name of this property.'''

        if _2345.SynchroniserPart.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SynchroniserPart. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_synchroniser_part.setter
    def selected_design_entity_of_type_synchroniser_part(self, value: '_2345.SynchroniserPart'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'SelectedDesignEntity' is the original name of this property.'''

        if _2346.SynchroniserSleeve.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to SynchroniserSleeve. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_synchroniser_sleeve.setter
    def selected_design_entity_of_type_synchroniser_sleeve(self, value: '_2346.SynchroniserSleeve'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_torque_converter(self) -> '_2347.TorqueConverter':
        '''TorqueConverter: 'SelectedDesignEntity' is the original name of this property.'''

        if _2347.TorqueConverter.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to TorqueConverter. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_torque_converter.setter
    def selected_design_entity_of_type_torque_converter(self, value: '_2347.TorqueConverter'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'SelectedDesignEntity' is the original name of this property.'''

        if _2348.TorqueConverterPump.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to TorqueConverterPump. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_torque_converter_pump.setter
    def selected_design_entity_of_type_torque_converter_pump(self, value: '_2348.TorqueConverterPump'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def selected_design_entity_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'SelectedDesignEntity' is the original name of this property.'''

        if _2350.TorqueConverterTurbine.TYPE not in self.wrapped.SelectedDesignEntity.__class__.__mro__:
            raise CastException('Failed to cast selected_design_entity to TorqueConverterTurbine. Expected: {}.'.format(self.wrapped.SelectedDesignEntity.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedDesignEntity.__class__)(self.wrapped.SelectedDesignEntity) if self.wrapped.SelectedDesignEntity is not None else None

    @selected_design_entity_of_type_torque_converter_turbine.setter
    def selected_design_entity_of_type_torque_converter_turbine(self, value: '_2350.TorqueConverterTurbine'):
        value = value.wrapped if value else None
        self.wrapped.SelectedDesignEntity = value

    @property
    def active_design(self) -> '_1947.Design':
        '''Design: 'ActiveDesign' is the original name of this property.'''

        return constructor.new(_1947.Design)(self.wrapped.ActiveDesign) if self.wrapped.ActiveDesign is not None else None

    @active_design.setter
    def active_design(self, value: '_1947.Design'):
        value = value.wrapped if value else None
        self.wrapped.ActiveDesign = value

    @property
    def open_designs(self) -> 'List[_1947.Design]':
        '''List[Design]: 'OpenDesigns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OpenDesigns, constructor.new(_1947.Design))
        return value

    @property
    def restart_geometry_modeller_flag(self) -> 'bool':
        '''bool: 'RestartGeometryModellerFlag' is the original name of this property.'''

        return self.wrapped.RestartGeometryModellerFlag

    @restart_geometry_modeller_flag.setter
    def restart_geometry_modeller_flag(self, value: 'bool'):
        self.wrapped.RestartGeometryModellerFlag = bool(value) if value else False

    @property
    def geometry_modeller_process_id(self) -> 'int':
        '''int: 'GeometryModellerProcessID' is the original name of this property.'''

        return self.wrapped.GeometryModellerProcessID

    @geometry_modeller_process_id.setter
    def geometry_modeller_process_id(self, value: 'int'):
        self.wrapped.GeometryModellerProcessID = int(value) if value else 0

    @property
    def restart_geometry_modeller_save_file(self) -> 'str':
        '''str: 'RestartGeometryModellerSaveFile' is the original name of this property.'''

        return self.wrapped.RestartGeometryModellerSaveFile

    @restart_geometry_modeller_save_file.setter
    def restart_geometry_modeller_save_file(self, value: 'str'):
        self.wrapped.RestartGeometryModellerSaveFile = str(value) if value else ''

    @property
    def color_of_new_problem_node_group(self) -> 'Color':
        '''Color: 'ColorOfNewProblemNodeGroup' is the original name of this property.'''

        value = conversion.pn_to_mp_color(self.wrapped.ColorOfNewProblemNodeGroup)
        return value

    @color_of_new_problem_node_group.setter
    def color_of_new_problem_node_group(self, value: 'Color'):
        value = value if value else None
        value = conversion.mp_to_pn_color(value)
        self.wrapped.ColorOfNewProblemNodeGroup = value

    @property
    def name_of_new_problem_node_group(self) -> 'str':
        '''str: 'NameOfNewProblemNodeGroup' is the original name of this property.'''

        return self.wrapped.NameOfNewProblemNodeGroup

    @name_of_new_problem_node_group.setter
    def name_of_new_problem_node_group(self, value: 'str'):
        self.wrapped.NameOfNewProblemNodeGroup = str(value) if value else ''

    @property
    def positions_of_problem_node_group(self) -> 'List[Vector3D]':
        '''List[Vector3D]: 'PositionsOfProblemNodeGroup' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PositionsOfProblemNodeGroup, Vector3D)
        return value

    @property
    def operation_mode(self) -> '_1561.OperationMode':
        '''OperationMode: 'OperationMode' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.OperationMode)
        return constructor.new(_1561.OperationMode)(value) if value is not None else None

    @operation_mode.setter
    def operation_mode(self, value: '_1561.OperationMode'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.OperationMode = value

    @property
    def is_connected_to_geometry_modeller(self) -> 'bool':
        '''bool: 'IsConnectedToGeometryModeller' is the original name of this property.'''

        return self.wrapped.IsConnectedToGeometryModeller

    @is_connected_to_geometry_modeller.setter
    def is_connected_to_geometry_modeller(self, value: 'bool'):
        self.wrapped.IsConnectedToGeometryModeller = bool(value) if value else False

    @property
    def process_id(self) -> 'int':
        '''int: 'ProcessId' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProcessId

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    @staticmethod
    def get_mastagui(process_id: 'int') -> 'MASTAGUI':
        ''' 'GetMASTAGUI' is the original name of this method.

        Args:
            process_id (int)

        Returns:
            mastapy.system_model_gui.MASTAGUI
        '''

        process_id = int(process_id)
        method_result = MASTAGUI.TYPE.GetMASTAGUI(process_id if process_id else 0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def resume(self):
        ''' 'Resume' is the original name of this method.'''

        self.wrapped.Resume()

    def pause(self):
        ''' 'Pause' is the original name of this method.'''

        self.wrapped.Pause()

    def start_remoting(self):
        ''' 'StartRemoting' is the original name of this method.'''

        self.wrapped.StartRemoting()

    def stop_remoting(self):
        ''' 'StopRemoting' is the original name of this method.'''

        self.wrapped.StopRemoting()

    def open_design_in_new_tab(self, design: '_1947.Design'):
        ''' 'OpenDesignInNewTab' is the original name of this method.

        Args:
            design (mastapy.system_model.Design)
        '''

        self.wrapped.OpenDesignInNewTab(design.wrapped if design else None)

    def select_tab(self, tab_text: 'str'):
        ''' 'SelectTab' is the original name of this method.

        Args:
            tab_text (str)
        '''

        tab_text = str(tab_text)
        self.wrapped.SelectTab(tab_text if tab_text else '')

    def move_selected_component(self, origin: 'Vector3D', axis: 'Vector3D'):
        ''' 'MoveSelectedComponent' is the original name of this method.

        Args:
            origin (Vector3D)
            axis (Vector3D)
        '''

        origin = conversion.mp_to_pn_vector3d(origin)
        axis = conversion.mp_to_pn_vector3d(axis)
        self.wrapped.MoveSelectedComponent(origin, axis)

    def run_command(self, command: 'str'):
        ''' 'RunCommand' is the original name of this method.

        Args:
            command (str)
        '''

        command = str(command)
        self.wrapped.RunCommand(command if command else '')

    def add_line_from_geometry_modeller(self, circles_on_axis: '_1291.CirclesOnAxis'):
        ''' 'AddLineFromGeometryModeller' is the original name of this method.

        Args:
            circles_on_axis (mastapy.math_utility.CirclesOnAxis)
        '''

        self.wrapped.AddLineFromGeometryModeller(circles_on_axis.wrapped if circles_on_axis else None)

    def show_boxes(self, small_box: 'List[Vector3D]', big_box: 'List[Vector3D]'):
        ''' 'ShowBoxes' is the original name of this method.

        Args:
            small_box (List[Vector3D])
            big_box (List[Vector3D])
        '''

        small_box = conversion.mp_to_pn_objects_in_list(small_box)
        big_box = conversion.mp_to_pn_objects_in_list(big_box)
        self.wrapped.ShowBoxes(small_box, big_box)

    def circle_pairs_from_geometry_modeller(self, preselection_circles: '_1291.CirclesOnAxis', selected_circles: 'List[_1291.CirclesOnAxis]'):
        ''' 'CirclePairsFromGeometryModeller' is the original name of this method.

        Args:
            preselection_circles (mastapy.math_utility.CirclesOnAxis)
            selected_circles (List[mastapy.math_utility.CirclesOnAxis])
        '''

        selected_circles = conversion.mp_to_pn_objects_in_list(selected_circles)
        self.wrapped.CirclePairsFromGeometryModeller(preselection_circles.wrapped if preselection_circles else None, selected_circles)

    def add_fe_substructure_from_data(self, vertices_and_facets: '_1310.FacetedBody', dimensions: 'Dict[str, _150.SpaceClaimDimension]', moniker: 'str'):
        ''' 'AddFESubstructureFromData' is the original name of this method.

        Args:
            vertices_and_facets (mastapy.math_utility.FacetedBody)
            dimensions (Dict[str, mastapy.nodal_analysis.geometry_modeller_link.SpaceClaimDimension])
            moniker (str)
        '''

        moniker = str(moniker)
        self.wrapped.AddFESubstructureFromData(vertices_and_facets.wrapped if vertices_and_facets else None, dimensions, moniker if moniker else '')

    def add_fe_substructure_from_file(self, length_scale: 'float', stl_file_name: 'str', dimensions: 'Dict[str, _150.SpaceClaimDimension]'):
        ''' 'AddFESubstructureFromFile' is the original name of this method.

        Args:
            length_scale (float)
            stl_file_name (str)
            dimensions (Dict[str, mastapy.nodal_analysis.geometry_modeller_link.SpaceClaimDimension])
        '''

        length_scale = float(length_scale)
        stl_file_name = str(stl_file_name)
        self.wrapped.AddFESubstructureFromFile(length_scale if length_scale else 0.0, stl_file_name if stl_file_name else '', dimensions)

    def flag_message_received(self):
        ''' 'FlagMessageReceived' is the original name of this method.'''

        self.wrapped.FlagMessageReceived()

    def geometry_modeller_document_loaded(self):
        ''' 'GeometryModellerDocumentLoaded' is the original name of this method.'''

        self.wrapped.GeometryModellerDocumentLoaded()

    def set_error(self, error: 'str'):
        ''' 'SetError' is the original name of this method.

        Args:
            error (str)
        '''

        error = str(error)
        self.wrapped.SetError(error if error else '')

    def new_dimensions(self, dimensions: 'Dict[str, _150.SpaceClaimDimension]'):
        ''' 'NewDimensions' is the original name of this method.

        Args:
            dimensions (Dict[str, mastapy.nodal_analysis.geometry_modeller_link.SpaceClaimDimension])
        '''

        self.wrapped.NewDimensions(dimensions)

    def create_geometry_modeller_dimension(self) -> '_150.SpaceClaimDimension':
        ''' 'CreateGeometryModellerDimension' is the original name of this method.

        Returns:
            mastapy.nodal_analysis.geometry_modeller_link.SpaceClaimDimension
        '''

        method_result = self.wrapped.CreateGeometryModellerDimension()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def new_mesh_data(self, vertices_and_facets: '_1310.FacetedBody'):
        ''' 'NewMeshData' is the original name of this method.

        Args:
            vertices_and_facets (mastapy.math_utility.FacetedBody)
        '''

        self.wrapped.NewMeshData.Overloads[_FACETED_BODY](vertices_and_facets.wrapped if vertices_and_facets else None)

    def new_mesh_data_from_file(self, stl_file_name: 'str'):
        ''' 'NewMeshData' is the original name of this method.

        Args:
            stl_file_name (str)
        '''

        stl_file_name = str(stl_file_name)
        self.wrapped.NewMeshData.Overloads[_STRING](stl_file_name if stl_file_name else '')

    def create_new_circles_on_axis(self) -> '_1291.CirclesOnAxis':
        ''' 'CreateNewCirclesOnAxis' is the original name of this method.

        Returns:
            mastapy.math_utility.CirclesOnAxis
        '''

        method_result = self.wrapped.CreateNewCirclesOnAxis()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_new_faceted_body(self) -> '_1310.FacetedBody':
        ''' 'CreateNewFacetedBody' is the original name of this method.

        Returns:
            mastapy.math_utility.FacetedBody
        '''

        method_result = self.wrapped.CreateNewFacetedBody()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
