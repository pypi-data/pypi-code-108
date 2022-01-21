'''list_with_selected_item.py

Implementations of 'ListWithSelectedItem' in Python.
As Python does not have an implicit operator, this is the next
best solution for implementing these types properly.
'''


from typing import List, Generic, TypeVar

from mastapy._internal import mixins, constructor, conversion
from mastapy._internal.python_net import python_net_import
from mastapy.gears.ltca.cylindrical import _817, _816
from mastapy.gears.manufacturing.cylindrical import _585
from mastapy.gears.manufacturing.bevel import _751
from mastapy.utility import _1393
from mastapy.utility.units_and_measurements import (
    _1403, _1395, _1396, _1397,
    _1401, _1402, _1404, _1398
)
from mastapy._internal.cast_exception import CastException
from mastapy.utility.units_and_measurements.measurements import (
    _1405, _1406, _1407, _1408,
    _1409, _1410, _1411, _1412,
    _1413, _1414, _1415, _1416,
    _1417, _1418, _1419, _1420,
    _1421, _1422, _1423, _1424,
    _1425, _1426, _1427, _1428,
    _1429, _1430, _1431, _1432,
    _1433, _1434, _1435, _1436,
    _1437, _1438, _1439, _1440,
    _1441, _1442, _1443, _1444,
    _1445, _1446, _1447, _1448,
    _1449, _1450, _1451, _1452,
    _1453, _1454, _1455, _1456,
    _1457, _1458, _1459, _1460,
    _1461, _1462, _1463, _1464,
    _1465, _1466, _1467, _1468,
    _1469, _1470, _1471, _1472,
    _1473, _1474, _1475, _1476,
    _1477, _1478, _1479, _1480,
    _1481, _1482, _1483, _1484,
    _1485, _1486, _1487, _1488,
    _1489, _1490, _1491, _1492,
    _1493, _1494, _1495, _1496,
    _1497, _1498, _1499, _1500,
    _1501, _1502, _1503, _1504,
    _1505, _1506, _1507, _1508,
    _1509, _1510, _1511, _1512
)
from mastapy.utility.file_access_helpers import _1586
from mastapy.system_model.part_model import (
    _2213, _2190, _2186, _2178,
    _2179, _2182, _2184, _2189,
    _2193, _2194, _2196, _2203,
    _2204, _2205, _2207, _2210,
    _2212, _2218, _2220
)
from mastapy.system_model.analyses_and_results.harmonic_analyses import (
    _5663, _5716, _5717, _5718,
    _5719, _5720, _5721, _5722,
    _5723, _5724, _5725, _5726,
    _5736, _5738, _5739, _5741,
    _5770, _5786, _5811
)
from mastapy._internal.tuple_with_name import TupleWithName
from mastapy.system_model.analyses_and_results.system_deflections import (
    _2494, _2429, _2436, _2441,
    _2455, _2459, _2474, _2475,
    _2476, _2489, _2498, _2503,
    _2506, _2509, _2542, _2548,
    _2551, _2571, _2574, _2480,
    _2481, _2482, _2485
)
from mastapy.system_model.part_model.gears import (
    _2272, _2254, _2256, _2260,
    _2262, _2264, _2266, _2269,
    _2275, _2277, _2279, _2281,
    _2282, _2284, _2286, _2288,
    _2292, _2294, _2253, _2255,
    _2257, _2258, _2259, _2261,
    _2263, _2265, _2267, _2268,
    _2270, _2274, _2276, _2278,
    _2280, _2283, _2285, _2287,
    _2289, _2290, _2291, _2293
)
from mastapy.system_model.fe import _2126, _2124, _2115
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.cycloidal import _2309, _2310
from mastapy.system_model.part_model.couplings import (
    _2319, _2322, _2324, _2327,
    _2329, _2330, _2336, _2338,
    _2341, _2344, _2345, _2346,
    _2348, _2350
)
from mastapy.system_model.fe.links import (
    _2159, _2160, _2162, _2163,
    _2164, _2165, _2166, _2167,
    _2168, _2169, _2170, _2171,
    _2172, _2173
)
from mastapy.system_model.part_model.part_groups import _2228
from mastapy.gears.gear_designs import _907
from mastapy.gears.gear_designs.zerol_bevel import _911
from mastapy.gears.gear_designs.worm import _916
from mastapy.gears.gear_designs.straight_bevel_diff import _920
from mastapy.gears.gear_designs.straight_bevel import _924
from mastapy.gears.gear_designs.spiral_bevel import _928
from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _932
from mastapy.gears.gear_designs.klingelnberg_hypoid import _936
from mastapy.gears.gear_designs.klingelnberg_conical import _940
from mastapy.gears.gear_designs.hypoid import _944
from mastapy.gears.gear_designs.face import _952
from mastapy.gears.gear_designs.cylindrical import _984, _995
from mastapy.gears.gear_designs.conical import _1103
from mastapy.gears.gear_designs.concept import _1125
from mastapy.gears.gear_designs.bevel import _1129
from mastapy.gears.gear_designs.agma_gleason_conical import _1142
from mastapy.system_model.analyses_and_results.load_case_groups import _5388, _5389
from mastapy.system_model.analyses_and_results.harmonic_analyses.results import _5827
from mastapy.system_model.analyses_and_results.static_loads import _6519, _6526
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4118

_ARRAY = python_net_import('System', 'Array')
_LIST_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.Utility.Property', 'ListWithSelectedItem')


__docformat__ = 'restructuredtext en'
__all__ = (
    'ListWithSelectedItem_str', 'ListWithSelectedItem_int',
    'ListWithSelectedItem_T', 'ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis',
    'ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis', 'ListWithSelectedItem_CylindricalSetManufacturingConfig',
    'ListWithSelectedItem_ConicalSetManufacturingConfig', 'ListWithSelectedItem_SystemDirectory',
    'ListWithSelectedItem_Unit', 'ListWithSelectedItem_MeasurementBase',
    'ListWithSelectedItem_ColumnTitle', 'ListWithSelectedItem_PowerLoad',
    'ListWithSelectedItem_AbstractPeriodicExcitationDetail', 'ListWithSelectedItem_TupleWithName',
    'ListWithSelectedItem_GearMeshSystemDeflection', 'ListWithSelectedItem_GearSet',
    'ListWithSelectedItem_FESubstructureNode', 'ListWithSelectedItem_Datum',
    'ListWithSelectedItem_Component', 'ListWithSelectedItem_FELink',
    'ListWithSelectedItem_FESubstructure', 'ListWithSelectedItem_CylindricalGear',
    'ListWithSelectedItem_GuideDxfModel', 'ListWithSelectedItem_ConcentricPartGroup',
    'ListWithSelectedItem_CylindricalGearSet', 'ListWithSelectedItem_GearSetDesign',
    'ListWithSelectedItem_ShaftHubConnection', 'ListWithSelectedItem_TSelectableItem',
    'ListWithSelectedItem_CylindricalGearSystemDeflection', 'ListWithSelectedItem_DesignState',
    'ListWithSelectedItem_FEPart', 'ListWithSelectedItem_TPartAnalysis',
    'ListWithSelectedItem_ResultLocationSelectionGroup', 'ListWithSelectedItem_StaticLoadCase',
    'ListWithSelectedItem_DutyCycle', 'ListWithSelectedItem_float',
    'ListWithSelectedItem_ElectricMachineDataSet', 'ListWithSelectedItem_PointLoad'
)


T = TypeVar('T')
TSelectableItem = TypeVar('TSelectableItem')
TPartAnalysis = TypeVar('TPartAnalysis')


class ListWithSelectedItem_str(str, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_str

    A specific implementation of 'ListWithSelectedItem' for 'str' types.
    '''

    __hash__ = None
    __qualname__ = 'str'

    def __new__(cls, instance_to_wrap: 'ListWithSelectedItem_str.TYPE'):
        return str.__new__(cls, instance_to_wrap.SelectedValue if instance_to_wrap.SelectedValue is not None else '')

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_str.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'str':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return str

    @property
    def selected_value(self) -> 'str':
        '''str: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[str]':
        '''List[str]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, str)
        return value


class ListWithSelectedItem_int(int, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_int

    A specific implementation of 'ListWithSelectedItem' for 'int' types.
    '''

    __hash__ = None
    __qualname__ = 'int'

    def __new__(cls, instance_to_wrap: 'ListWithSelectedItem_int.TYPE'):
        return int.__new__(cls, instance_to_wrap.SelectedValue if instance_to_wrap.SelectedValue is not None else 0)

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_int.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'int':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return int

    @property
    def selected_value(self) -> 'int':
        '''int: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[int]':
        '''List[int]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, int)
        return value


class ListWithSelectedItem_T(Generic[T], mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_T

    A specific implementation of 'ListWithSelectedItem' for 'T' types.
    '''

    __hash__ = None
    __qualname__ = 'T'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_T.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'T':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return T

    @property
    def selected_value(self) -> 'T':
        '''T: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[T]':
        '''List[T]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues)
        return value


class ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis(_817.CylindricalGearMeshLoadDistributionAnalysis, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalGearMeshLoadDistributionAnalysis' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGearMeshLoadDistributionAnalysis'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_817.CylindricalGearMeshLoadDistributionAnalysis.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _817.CylindricalGearMeshLoadDistributionAnalysis.TYPE

    @property
    def selected_value(self) -> '_817.CylindricalGearMeshLoadDistributionAnalysis':
        '''CylindricalGearMeshLoadDistributionAnalysis: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_817.CylindricalGearMeshLoadDistributionAnalysis)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_817.CylindricalGearMeshLoadDistributionAnalysis]':
        '''List[CylindricalGearMeshLoadDistributionAnalysis]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_817.CylindricalGearMeshLoadDistributionAnalysis))
        return value


class ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis(_816.CylindricalGearLoadDistributionAnalysis, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalGearLoadDistributionAnalysis' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGearLoadDistributionAnalysis'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_816.CylindricalGearLoadDistributionAnalysis.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _816.CylindricalGearLoadDistributionAnalysis.TYPE

    @property
    def selected_value(self) -> '_816.CylindricalGearLoadDistributionAnalysis':
        '''CylindricalGearLoadDistributionAnalysis: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_816.CylindricalGearLoadDistributionAnalysis)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_816.CylindricalGearLoadDistributionAnalysis]':
        '''List[CylindricalGearLoadDistributionAnalysis]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_816.CylindricalGearLoadDistributionAnalysis))
        return value


class ListWithSelectedItem_CylindricalSetManufacturingConfig(_585.CylindricalSetManufacturingConfig, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalSetManufacturingConfig

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalSetManufacturingConfig' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalSetManufacturingConfig'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalSetManufacturingConfig.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_585.CylindricalSetManufacturingConfig.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _585.CylindricalSetManufacturingConfig.TYPE

    @property
    def selected_value(self) -> '_585.CylindricalSetManufacturingConfig':
        '''CylindricalSetManufacturingConfig: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_585.CylindricalSetManufacturingConfig)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_585.CylindricalSetManufacturingConfig]':
        '''List[CylindricalSetManufacturingConfig]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_585.CylindricalSetManufacturingConfig))
        return value


class ListWithSelectedItem_ConicalSetManufacturingConfig(_751.ConicalSetManufacturingConfig, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ConicalSetManufacturingConfig

    A specific implementation of 'ListWithSelectedItem' for 'ConicalSetManufacturingConfig' types.
    '''

    __hash__ = None
    __qualname__ = 'ConicalSetManufacturingConfig'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ConicalSetManufacturingConfig.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_751.ConicalSetManufacturingConfig.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _751.ConicalSetManufacturingConfig.TYPE

    @property
    def selected_value(self) -> '_751.ConicalSetManufacturingConfig':
        '''ConicalSetManufacturingConfig: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_751.ConicalSetManufacturingConfig)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_751.ConicalSetManufacturingConfig]':
        '''List[ConicalSetManufacturingConfig]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_751.ConicalSetManufacturingConfig))
        return value


class ListWithSelectedItem_SystemDirectory(_1393.SystemDirectory, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_SystemDirectory

    A specific implementation of 'ListWithSelectedItem' for 'SystemDirectory' types.
    '''

    __hash__ = None
    __qualname__ = 'SystemDirectory'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_SystemDirectory.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_1393.SystemDirectory.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1393.SystemDirectory.TYPE

    @property
    def selected_value(self) -> '_1393.SystemDirectory':
        '''SystemDirectory: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1393.SystemDirectory)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_1393.SystemDirectory]':
        '''List[SystemDirectory]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_1393.SystemDirectory))
        return value


class ListWithSelectedItem_Unit(_1403.Unit, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_Unit

    A specific implementation of 'ListWithSelectedItem' for 'Unit' types.
    '''

    __hash__ = None
    __qualname__ = 'Unit'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_Unit.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_1403.Unit.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1403.Unit.TYPE

    @property
    def selected_value(self) -> '_1403.Unit':
        '''Unit: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1403.Unit.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Unit. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_1403.Unit]':
        '''List[Unit]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_1403.Unit))
        return value


class ListWithSelectedItem_MeasurementBase(_1398.MeasurementBase, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_MeasurementBase

    A specific implementation of 'ListWithSelectedItem' for 'MeasurementBase' types.
    '''

    __hash__ = None
    __qualname__ = 'MeasurementBase'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_MeasurementBase.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_1398.MeasurementBase.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1398.MeasurementBase.TYPE

    @property
    def selected_value(self) -> '_1398.MeasurementBase':
        '''MeasurementBase: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1398.MeasurementBase.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MeasurementBase. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_acceleration(self) -> '_1405.Acceleration':
        '''Acceleration: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1405.Acceleration.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Acceleration. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angle(self) -> '_1406.Angle':
        '''Angle: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1406.Angle.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Angle. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angle_per_unit_temperature(self) -> '_1407.AnglePerUnitTemperature':
        '''AnglePerUnitTemperature: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1407.AnglePerUnitTemperature.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AnglePerUnitTemperature. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angle_small(self) -> '_1408.AngleSmall':
        '''AngleSmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1408.AngleSmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngleSmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angle_very_small(self) -> '_1409.AngleVerySmall':
        '''AngleVerySmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1409.AngleVerySmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngleVerySmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angular_acceleration(self) -> '_1410.AngularAcceleration':
        '''AngularAcceleration: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1410.AngularAcceleration.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngularAcceleration. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angular_compliance(self) -> '_1411.AngularCompliance':
        '''AngularCompliance: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1411.AngularCompliance.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngularCompliance. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angular_jerk(self) -> '_1412.AngularJerk':
        '''AngularJerk: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1412.AngularJerk.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngularJerk. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angular_stiffness(self) -> '_1413.AngularStiffness':
        '''AngularStiffness: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1413.AngularStiffness.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngularStiffness. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_angular_velocity(self) -> '_1414.AngularVelocity':
        '''AngularVelocity: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1414.AngularVelocity.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AngularVelocity. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_area(self) -> '_1415.Area':
        '''Area: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1415.Area.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Area. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_area_small(self) -> '_1416.AreaSmall':
        '''AreaSmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1416.AreaSmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AreaSmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cycles(self) -> '_1417.Cycles':
        '''Cycles: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1417.Cycles.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Cycles. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_damage(self) -> '_1418.Damage':
        '''Damage: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1418.Damage.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Damage. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_damage_rate(self) -> '_1419.DamageRate':
        '''DamageRate: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1419.DamageRate.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to DamageRate. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_data_size(self) -> '_1420.DataSize':
        '''DataSize: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1420.DataSize.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to DataSize. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_decibel(self) -> '_1421.Decibel':
        '''Decibel: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1421.Decibel.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Decibel. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_density(self) -> '_1422.Density':
        '''Density: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1422.Density.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Density. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_energy(self) -> '_1423.Energy':
        '''Energy: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1423.Energy.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Energy. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_energy_per_unit_area(self) -> '_1424.EnergyPerUnitArea':
        '''EnergyPerUnitArea: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1424.EnergyPerUnitArea.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to EnergyPerUnitArea. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_energy_per_unit_area_small(self) -> '_1425.EnergyPerUnitAreaSmall':
        '''EnergyPerUnitAreaSmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1425.EnergyPerUnitAreaSmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to EnergyPerUnitAreaSmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_energy_small(self) -> '_1426.EnergySmall':
        '''EnergySmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1426.EnergySmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to EnergySmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_enum(self) -> '_1427.Enum':
        '''Enum: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1427.Enum.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Enum. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_flow_rate(self) -> '_1428.FlowRate':
        '''FlowRate: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1428.FlowRate.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FlowRate. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_force(self) -> '_1429.Force':
        '''Force: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1429.Force.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Force. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_force_per_unit_length(self) -> '_1430.ForcePerUnitLength':
        '''ForcePerUnitLength: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1430.ForcePerUnitLength.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ForcePerUnitLength. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_force_per_unit_pressure(self) -> '_1431.ForcePerUnitPressure':
        '''ForcePerUnitPressure: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1431.ForcePerUnitPressure.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ForcePerUnitPressure. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_force_per_unit_temperature(self) -> '_1432.ForcePerUnitTemperature':
        '''ForcePerUnitTemperature: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1432.ForcePerUnitTemperature.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ForcePerUnitTemperature. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_fraction_measurement_base(self) -> '_1433.FractionMeasurementBase':
        '''FractionMeasurementBase: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1433.FractionMeasurementBase.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FractionMeasurementBase. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_frequency(self) -> '_1434.Frequency':
        '''Frequency: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1434.Frequency.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Frequency. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_fuel_consumption_engine(self) -> '_1435.FuelConsumptionEngine':
        '''FuelConsumptionEngine: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1435.FuelConsumptionEngine.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FuelConsumptionEngine. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_fuel_efficiency_vehicle(self) -> '_1436.FuelEfficiencyVehicle':
        '''FuelEfficiencyVehicle: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1436.FuelEfficiencyVehicle.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FuelEfficiencyVehicle. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gradient(self) -> '_1437.Gradient':
        '''Gradient: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1437.Gradient.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Gradient. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_heat_conductivity(self) -> '_1438.HeatConductivity':
        '''HeatConductivity: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1438.HeatConductivity.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HeatConductivity. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_heat_transfer(self) -> '_1439.HeatTransfer':
        '''HeatTransfer: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1439.HeatTransfer.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HeatTransfer. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_heat_transfer_coefficient_for_plastic_gear_tooth(self) -> '_1440.HeatTransferCoefficientForPlasticGearTooth':
        '''HeatTransferCoefficientForPlasticGearTooth: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1440.HeatTransferCoefficientForPlasticGearTooth.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HeatTransferCoefficientForPlasticGearTooth. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_heat_transfer_resistance(self) -> '_1441.HeatTransferResistance':
        '''HeatTransferResistance: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1441.HeatTransferResistance.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HeatTransferResistance. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_impulse(self) -> '_1442.Impulse':
        '''Impulse: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1442.Impulse.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Impulse. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_index(self) -> '_1443.Index':
        '''Index: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1443.Index.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Index. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_integer(self) -> '_1444.Integer':
        '''Integer: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1444.Integer.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Integer. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_inverse_short_length(self) -> '_1445.InverseShortLength':
        '''InverseShortLength: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1445.InverseShortLength.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to InverseShortLength. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_inverse_short_time(self) -> '_1446.InverseShortTime':
        '''InverseShortTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1446.InverseShortTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to InverseShortTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_jerk(self) -> '_1447.Jerk':
        '''Jerk: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1447.Jerk.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Jerk. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_kinematic_viscosity(self) -> '_1448.KinematicViscosity':
        '''KinematicViscosity: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1448.KinematicViscosity.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KinematicViscosity. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_long(self) -> '_1449.LengthLong':
        '''LengthLong: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1449.LengthLong.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthLong. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_medium(self) -> '_1450.LengthMedium':
        '''LengthMedium: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1450.LengthMedium.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthMedium. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_per_unit_temperature(self) -> '_1451.LengthPerUnitTemperature':
        '''LengthPerUnitTemperature: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1451.LengthPerUnitTemperature.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthPerUnitTemperature. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_short(self) -> '_1452.LengthShort':
        '''LengthShort: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1452.LengthShort.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthShort. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_to_the_fourth(self) -> '_1453.LengthToTheFourth':
        '''LengthToTheFourth: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1453.LengthToTheFourth.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthToTheFourth. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_very_long(self) -> '_1454.LengthVeryLong':
        '''LengthVeryLong: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1454.LengthVeryLong.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthVeryLong. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_very_short(self) -> '_1455.LengthVeryShort':
        '''LengthVeryShort: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1455.LengthVeryShort.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthVeryShort. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_length_very_short_per_length_short(self) -> '_1456.LengthVeryShortPerLengthShort':
        '''LengthVeryShortPerLengthShort: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1456.LengthVeryShortPerLengthShort.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LengthVeryShortPerLengthShort. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_linear_angular_damping(self) -> '_1457.LinearAngularDamping':
        '''LinearAngularDamping: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1457.LinearAngularDamping.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LinearAngularDamping. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_linear_angular_stiffness_cross_term(self) -> '_1458.LinearAngularStiffnessCrossTerm':
        '''LinearAngularStiffnessCrossTerm: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1458.LinearAngularStiffnessCrossTerm.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LinearAngularStiffnessCrossTerm. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_linear_damping(self) -> '_1459.LinearDamping':
        '''LinearDamping: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1459.LinearDamping.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LinearDamping. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_linear_flexibility(self) -> '_1460.LinearFlexibility':
        '''LinearFlexibility: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1460.LinearFlexibility.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LinearFlexibility. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_linear_stiffness(self) -> '_1461.LinearStiffness':
        '''LinearStiffness: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1461.LinearStiffness.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to LinearStiffness. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_mass(self) -> '_1462.Mass':
        '''Mass: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1462.Mass.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Mass. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_mass_per_unit_length(self) -> '_1463.MassPerUnitLength':
        '''MassPerUnitLength: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1463.MassPerUnitLength.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MassPerUnitLength. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_mass_per_unit_time(self) -> '_1464.MassPerUnitTime':
        '''MassPerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1464.MassPerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MassPerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_moment_of_inertia(self) -> '_1465.MomentOfInertia':
        '''MomentOfInertia: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1465.MomentOfInertia.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MomentOfInertia. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_moment_of_inertia_per_unit_length(self) -> '_1466.MomentOfInertiaPerUnitLength':
        '''MomentOfInertiaPerUnitLength: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1466.MomentOfInertiaPerUnitLength.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MomentOfInertiaPerUnitLength. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_moment_per_unit_pressure(self) -> '_1467.MomentPerUnitPressure':
        '''MomentPerUnitPressure: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1467.MomentPerUnitPressure.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MomentPerUnitPressure. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_number(self) -> '_1468.Number':
        '''Number: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1468.Number.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Number. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_percentage(self) -> '_1469.Percentage':
        '''Percentage: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1469.Percentage.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Percentage. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power(self) -> '_1470.Power':
        '''Power: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1470.Power.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Power. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_per_small_area(self) -> '_1471.PowerPerSmallArea':
        '''PowerPerSmallArea: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1471.PowerPerSmallArea.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerPerSmallArea. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_per_unit_time(self) -> '_1472.PowerPerUnitTime':
        '''PowerPerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1472.PowerPerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerPerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_small(self) -> '_1473.PowerSmall':
        '''PowerSmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1473.PowerSmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerSmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_small_per_area(self) -> '_1474.PowerSmallPerArea':
        '''PowerSmallPerArea: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1474.PowerSmallPerArea.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerSmallPerArea. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_small_per_unit_area_per_unit_time(self) -> '_1475.PowerSmallPerUnitAreaPerUnitTime':
        '''PowerSmallPerUnitAreaPerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1475.PowerSmallPerUnitAreaPerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerSmallPerUnitAreaPerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_small_per_unit_time(self) -> '_1476.PowerSmallPerUnitTime':
        '''PowerSmallPerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1476.PowerSmallPerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerSmallPerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_pressure(self) -> '_1477.Pressure':
        '''Pressure: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1477.Pressure.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Pressure. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_pressure_per_unit_time(self) -> '_1478.PressurePerUnitTime':
        '''PressurePerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1478.PressurePerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PressurePerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_pressure_velocity_product(self) -> '_1479.PressureVelocityProduct':
        '''PressureVelocityProduct: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1479.PressureVelocityProduct.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PressureVelocityProduct. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_pressure_viscosity_coefficient(self) -> '_1480.PressureViscosityCoefficient':
        '''PressureViscosityCoefficient: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1480.PressureViscosityCoefficient.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PressureViscosityCoefficient. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_price(self) -> '_1481.Price':
        '''Price: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1481.Price.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Price. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_quadratic_angular_damping(self) -> '_1482.QuadraticAngularDamping':
        '''QuadraticAngularDamping: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1482.QuadraticAngularDamping.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to QuadraticAngularDamping. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_quadratic_drag(self) -> '_1483.QuadraticDrag':
        '''QuadraticDrag: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1483.QuadraticDrag.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to QuadraticDrag. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_rescaled_measurement(self) -> '_1484.RescaledMeasurement':
        '''RescaledMeasurement: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1484.RescaledMeasurement.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to RescaledMeasurement. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_rotatum(self) -> '_1485.Rotatum':
        '''Rotatum: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1485.Rotatum.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Rotatum. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_safety_factor(self) -> '_1486.SafetyFactor':
        '''SafetyFactor: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1486.SafetyFactor.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SafetyFactor. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_specific_acoustic_impedance(self) -> '_1487.SpecificAcousticImpedance':
        '''SpecificAcousticImpedance: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1487.SpecificAcousticImpedance.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpecificAcousticImpedance. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_specific_heat(self) -> '_1488.SpecificHeat':
        '''SpecificHeat: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1488.SpecificHeat.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpecificHeat. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_square_root_of_unit_force_per_unit_area(self) -> '_1489.SquareRootOfUnitForcePerUnitArea':
        '''SquareRootOfUnitForcePerUnitArea: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1489.SquareRootOfUnitForcePerUnitArea.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SquareRootOfUnitForcePerUnitArea. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_stiffness_per_unit_face_width(self) -> '_1490.StiffnessPerUnitFaceWidth':
        '''StiffnessPerUnitFaceWidth: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1490.StiffnessPerUnitFaceWidth.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StiffnessPerUnitFaceWidth. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_stress(self) -> '_1491.Stress':
        '''Stress: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1491.Stress.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Stress. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_temperature(self) -> '_1492.Temperature':
        '''Temperature: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1492.Temperature.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Temperature. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_temperature_difference(self) -> '_1493.TemperatureDifference':
        '''TemperatureDifference: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1493.TemperatureDifference.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TemperatureDifference. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_temperature_per_unit_time(self) -> '_1494.TemperaturePerUnitTime':
        '''TemperaturePerUnitTime: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1494.TemperaturePerUnitTime.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TemperaturePerUnitTime. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_text(self) -> '_1495.Text':
        '''Text: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1495.Text.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Text. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_thermal_contact_coefficient(self) -> '_1496.ThermalContactCoefficient':
        '''ThermalContactCoefficient: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1496.ThermalContactCoefficient.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ThermalContactCoefficient. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_thermal_expansion_coefficient(self) -> '_1497.ThermalExpansionCoefficient':
        '''ThermalExpansionCoefficient: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1497.ThermalExpansionCoefficient.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ThermalExpansionCoefficient. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_thermo_elastic_factor(self) -> '_1498.ThermoElasticFactor':
        '''ThermoElasticFactor: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1498.ThermoElasticFactor.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ThermoElasticFactor. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_time(self) -> '_1499.Time':
        '''Time: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1499.Time.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Time. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_time_short(self) -> '_1500.TimeShort':
        '''TimeShort: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1500.TimeShort.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TimeShort. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_time_very_short(self) -> '_1501.TimeVeryShort':
        '''TimeVeryShort: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1501.TimeVeryShort.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TimeVeryShort. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque(self) -> '_1502.Torque':
        '''Torque: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1502.Torque.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Torque. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque_converter_inverse_k(self) -> '_1503.TorqueConverterInverseK':
        '''TorqueConverterInverseK: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1503.TorqueConverterInverseK.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TorqueConverterInverseK. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque_converter_k(self) -> '_1504.TorqueConverterK':
        '''TorqueConverterK: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1504.TorqueConverterK.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TorqueConverterK. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque_per_unit_temperature(self) -> '_1505.TorquePerUnitTemperature':
        '''TorquePerUnitTemperature: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1505.TorquePerUnitTemperature.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TorquePerUnitTemperature. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_velocity(self) -> '_1506.Velocity':
        '''Velocity: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1506.Velocity.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Velocity. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_velocity_small(self) -> '_1507.VelocitySmall':
        '''VelocitySmall: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1507.VelocitySmall.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to VelocitySmall. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_viscosity(self) -> '_1508.Viscosity':
        '''Viscosity: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1508.Viscosity.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Viscosity. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_voltage(self) -> '_1509.Voltage':
        '''Voltage: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1509.Voltage.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Voltage. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_volume(self) -> '_1510.Volume':
        '''Volume: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1510.Volume.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Volume. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_wear_coefficient(self) -> '_1511.WearCoefficient':
        '''WearCoefficient: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1511.WearCoefficient.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to WearCoefficient. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_yank(self) -> '_1512.Yank':
        '''Yank: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1512.Yank.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Yank. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_1398.MeasurementBase]':
        '''List[MeasurementBase]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_1398.MeasurementBase))
        return value


class ListWithSelectedItem_ColumnTitle(_1586.ColumnTitle, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ColumnTitle

    A specific implementation of 'ListWithSelectedItem' for 'ColumnTitle' types.
    '''

    __hash__ = None
    __qualname__ = 'ColumnTitle'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ColumnTitle.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_1586.ColumnTitle.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1586.ColumnTitle.TYPE

    @property
    def selected_value(self) -> '_1586.ColumnTitle':
        '''ColumnTitle: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1586.ColumnTitle)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_1586.ColumnTitle]':
        '''List[ColumnTitle]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_1586.ColumnTitle))
        return value


class ListWithSelectedItem_PowerLoad(_2213.PowerLoad, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_PowerLoad

    A specific implementation of 'ListWithSelectedItem' for 'PowerLoad' types.
    '''

    __hash__ = None
    __qualname__ = 'PowerLoad'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_PowerLoad.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2213.PowerLoad.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2213.PowerLoad.TYPE

    @property
    def selected_value(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2213.PowerLoad]':
        '''List[PowerLoad]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2213.PowerLoad))
        return value


class ListWithSelectedItem_AbstractPeriodicExcitationDetail(_5663.AbstractPeriodicExcitationDetail, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_AbstractPeriodicExcitationDetail

    A specific implementation of 'ListWithSelectedItem' for 'AbstractPeriodicExcitationDetail' types.
    '''

    __hash__ = None
    __qualname__ = 'AbstractPeriodicExcitationDetail'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_AbstractPeriodicExcitationDetail.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_5663.AbstractPeriodicExcitationDetail.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _5663.AbstractPeriodicExcitationDetail.TYPE

    @property
    def selected_value(self) -> '_5663.AbstractPeriodicExcitationDetail':
        '''AbstractPeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5663.AbstractPeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AbstractPeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_periodic_excitation_detail(self) -> '_5716.ElectricMachinePeriodicExcitationDetail':
        '''ElectricMachinePeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5716.ElectricMachinePeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachinePeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_rotor_x_force_periodic_excitation_detail(self) -> '_5717.ElectricMachineRotorXForcePeriodicExcitationDetail':
        '''ElectricMachineRotorXForcePeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5717.ElectricMachineRotorXForcePeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineRotorXForcePeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_rotor_x_moment_periodic_excitation_detail(self) -> '_5718.ElectricMachineRotorXMomentPeriodicExcitationDetail':
        '''ElectricMachineRotorXMomentPeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5718.ElectricMachineRotorXMomentPeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineRotorXMomentPeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_rotor_y_force_periodic_excitation_detail(self) -> '_5719.ElectricMachineRotorYForcePeriodicExcitationDetail':
        '''ElectricMachineRotorYForcePeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5719.ElectricMachineRotorYForcePeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineRotorYForcePeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_rotor_y_moment_periodic_excitation_detail(self) -> '_5720.ElectricMachineRotorYMomentPeriodicExcitationDetail':
        '''ElectricMachineRotorYMomentPeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5720.ElectricMachineRotorYMomentPeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineRotorYMomentPeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_rotor_z_force_periodic_excitation_detail(self) -> '_5721.ElectricMachineRotorZForcePeriodicExcitationDetail':
        '''ElectricMachineRotorZForcePeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5721.ElectricMachineRotorZForcePeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineRotorZForcePeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_stator_tooth_axial_loads_excitation_detail(self) -> '_5722.ElectricMachineStatorToothAxialLoadsExcitationDetail':
        '''ElectricMachineStatorToothAxialLoadsExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5722.ElectricMachineStatorToothAxialLoadsExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineStatorToothAxialLoadsExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_stator_tooth_loads_excitation_detail(self) -> '_5723.ElectricMachineStatorToothLoadsExcitationDetail':
        '''ElectricMachineStatorToothLoadsExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5723.ElectricMachineStatorToothLoadsExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineStatorToothLoadsExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_stator_tooth_radial_loads_excitation_detail(self) -> '_5724.ElectricMachineStatorToothRadialLoadsExcitationDetail':
        '''ElectricMachineStatorToothRadialLoadsExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5724.ElectricMachineStatorToothRadialLoadsExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineStatorToothRadialLoadsExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_stator_tooth_tangential_loads_excitation_detail(self) -> '_5725.ElectricMachineStatorToothTangentialLoadsExcitationDetail':
        '''ElectricMachineStatorToothTangentialLoadsExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5725.ElectricMachineStatorToothTangentialLoadsExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineStatorToothTangentialLoadsExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_torque_ripple_periodic_excitation_detail(self) -> '_5726.ElectricMachineTorqueRipplePeriodicExcitationDetail':
        '''ElectricMachineTorqueRipplePeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5726.ElectricMachineTorqueRipplePeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineTorqueRipplePeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear_mesh_excitation_detail(self) -> '_5736.GearMeshExcitationDetail':
        '''GearMeshExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5736.GearMeshExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearMeshExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear_mesh_misalignment_excitation_detail(self) -> '_5738.GearMeshMisalignmentExcitationDetail':
        '''GearMeshMisalignmentExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5738.GearMeshMisalignmentExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearMeshMisalignmentExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear_mesh_te_excitation_detail(self) -> '_5739.GearMeshTEExcitationDetail':
        '''GearMeshTEExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5739.GearMeshTEExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearMeshTEExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_general_periodic_excitation_detail(self) -> '_5741.GeneralPeriodicExcitationDetail':
        '''GeneralPeriodicExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5741.GeneralPeriodicExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GeneralPeriodicExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_periodic_excitation_with_reference_shaft(self) -> '_5770.PeriodicExcitationWithReferenceShaft':
        '''PeriodicExcitationWithReferenceShaft: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5770.PeriodicExcitationWithReferenceShaft.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PeriodicExcitationWithReferenceShaft. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_single_node_periodic_excitation_with_reference_shaft(self) -> '_5786.SingleNodePeriodicExcitationWithReferenceShaft':
        '''SingleNodePeriodicExcitationWithReferenceShaft: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5786.SingleNodePeriodicExcitationWithReferenceShaft.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SingleNodePeriodicExcitationWithReferenceShaft. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_unbalanced_mass_excitation_detail(self) -> '_5811.UnbalancedMassExcitationDetail':
        '''UnbalancedMassExcitationDetail: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5811.UnbalancedMassExcitationDetail.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to UnbalancedMassExcitationDetail. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_5663.AbstractPeriodicExcitationDetail]':
        '''List[AbstractPeriodicExcitationDetail]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_5663.AbstractPeriodicExcitationDetail))
        return value


class ListWithSelectedItem_TupleWithName(TupleWithName, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_TupleWithName

    A specific implementation of 'ListWithSelectedItem' for 'TupleWithName' types.
    '''

    __hash__ = None
    __qualname__ = 'TupleWithName'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_TupleWithName.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'TupleWithName.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return TupleWithName.TYPE

    @property
    def selected_value(self) -> 'TupleWithName':
        '''TupleWithName: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_tuple_with_name(self.enclosing.SelectedValue, (None))
        return constructor.new(TupleWithName)(value) if value is not None else None

    @property
    def available_values(self) -> 'TupleWithName':
        '''TupleWithName: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(TupleWithName))
        return constructor.new(TupleWithName)(value) if value is not None else None


class ListWithSelectedItem_GearMeshSystemDeflection(_2494.GearMeshSystemDeflection, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_GearMeshSystemDeflection

    A specific implementation of 'ListWithSelectedItem' for 'GearMeshSystemDeflection' types.
    '''

    __hash__ = None
    __qualname__ = 'GearMeshSystemDeflection'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_GearMeshSystemDeflection.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2494.GearMeshSystemDeflection.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2494.GearMeshSystemDeflection.TYPE

    @property
    def selected_value(self) -> '_2494.GearMeshSystemDeflection':
        '''GearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2494.GearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_agma_gleason_conical_gear_mesh_system_deflection(self) -> '_2429.AGMAGleasonConicalGearMeshSystemDeflection':
        '''AGMAGleasonConicalGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2429.AGMAGleasonConicalGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AGMAGleasonConicalGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_differential_gear_mesh_system_deflection(self) -> '_2436.BevelDifferentialGearMeshSystemDeflection':
        '''BevelDifferentialGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2436.BevelDifferentialGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelDifferentialGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_gear_mesh_system_deflection(self) -> '_2441.BevelGearMeshSystemDeflection':
        '''BevelGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2441.BevelGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_concept_gear_mesh_system_deflection(self) -> '_2455.ConceptGearMeshSystemDeflection':
        '''ConceptGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2455.ConceptGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConceptGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_conical_gear_mesh_system_deflection(self) -> '_2459.ConicalGearMeshSystemDeflection':
        '''ConicalGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2459.ConicalGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConicalGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_mesh_system_deflection(self) -> '_2474.CylindricalGearMeshSystemDeflection':
        '''CylindricalGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2474.CylindricalGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_mesh_system_deflection_timestep(self) -> '_2475.CylindricalGearMeshSystemDeflectionTimestep':
        '''CylindricalGearMeshSystemDeflectionTimestep: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2475.CylindricalGearMeshSystemDeflectionTimestep.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearMeshSystemDeflectionTimestep. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_mesh_system_deflection_with_ltca_results(self) -> '_2476.CylindricalGearMeshSystemDeflectionWithLTCAResults':
        '''CylindricalGearMeshSystemDeflectionWithLTCAResults: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2476.CylindricalGearMeshSystemDeflectionWithLTCAResults.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearMeshSystemDeflectionWithLTCAResults. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_face_gear_mesh_system_deflection(self) -> '_2489.FaceGearMeshSystemDeflection':
        '''FaceGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2489.FaceGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FaceGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_hypoid_gear_mesh_system_deflection(self) -> '_2498.HypoidGearMeshSystemDeflection':
        '''HypoidGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2498.HypoidGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HypoidGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh_system_deflection(self) -> '_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidConicalGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidConicalGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh_system_deflection(self) -> '_2506.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2506.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_system_deflection(self) -> '_2509.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2509.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_spiral_bevel_gear_mesh_system_deflection(self) -> '_2542.SpiralBevelGearMeshSystemDeflection':
        '''SpiralBevelGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2542.SpiralBevelGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpiralBevelGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_diff_gear_mesh_system_deflection(self) -> '_2548.StraightBevelDiffGearMeshSystemDeflection':
        '''StraightBevelDiffGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2548.StraightBevelDiffGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelDiffGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_gear_mesh_system_deflection(self) -> '_2551.StraightBevelGearMeshSystemDeflection':
        '''StraightBevelGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2551.StraightBevelGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_worm_gear_mesh_system_deflection(self) -> '_2571.WormGearMeshSystemDeflection':
        '''WormGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2571.WormGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to WormGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_zerol_bevel_gear_mesh_system_deflection(self) -> '_2574.ZerolBevelGearMeshSystemDeflection':
        '''ZerolBevelGearMeshSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2574.ZerolBevelGearMeshSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ZerolBevelGearMeshSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2494.GearMeshSystemDeflection]':
        '''List[GearMeshSystemDeflection]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2494.GearMeshSystemDeflection))
        return value


class ListWithSelectedItem_GearSet(_2272.GearSet, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_GearSet

    A specific implementation of 'ListWithSelectedItem' for 'GearSet' types.
    '''

    __hash__ = None
    __qualname__ = 'GearSet'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_GearSet.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2272.GearSet.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2272.GearSet.TYPE

    @property
    def selected_value(self) -> '_2272.GearSet':
        '''GearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2272.GearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_agma_gleason_conical_gear_set(self) -> '_2254.AGMAGleasonConicalGearSet':
        '''AGMAGleasonConicalGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2254.AGMAGleasonConicalGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AGMAGleasonConicalGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_differential_gear_set(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2256.BevelDifferentialGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelDifferentialGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_gear_set(self) -> '_2260.BevelGearSet':
        '''BevelGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2260.BevelGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_concept_gear_set(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2262.ConceptGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConceptGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_conical_gear_set(self) -> '_2264.ConicalGearSet':
        '''ConicalGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2264.ConicalGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConicalGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_set(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_face_gear_set(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2269.FaceGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FaceGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_hypoid_gear_set(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2275.HypoidGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HypoidGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_conical_gear_set(self) -> '_2277.KlingelnbergCycloPalloidConicalGearSet':
        '''KlingelnbergCycloPalloidConicalGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2277.KlingelnbergCycloPalloidConicalGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidConicalGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2279.KlingelnbergCycloPalloidHypoidGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidHypoidGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2281.KlingelnbergCycloPalloidSpiralBevelGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidSpiralBevelGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_planetary_gear_set(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2282.PlanetaryGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PlanetaryGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_spiral_bevel_gear_set(self) -> '_2284.SpiralBevelGearSet':
        '''SpiralBevelGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2284.SpiralBevelGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpiralBevelGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_diff_gear_set(self) -> '_2286.StraightBevelDiffGearSet':
        '''StraightBevelDiffGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2286.StraightBevelDiffGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelDiffGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_gear_set(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2288.StraightBevelGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_worm_gear_set(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2292.WormGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to WormGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_zerol_bevel_gear_set(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2294.ZerolBevelGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ZerolBevelGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2272.GearSet]':
        '''List[GearSet]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2272.GearSet))
        return value


class ListWithSelectedItem_FESubstructureNode(_2126.FESubstructureNode, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_FESubstructureNode

    A specific implementation of 'ListWithSelectedItem' for 'FESubstructureNode' types.
    '''

    __hash__ = None
    __qualname__ = 'FESubstructureNode'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_FESubstructureNode.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2126.FESubstructureNode.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2126.FESubstructureNode.TYPE

    @property
    def selected_value(self) -> '_2126.FESubstructureNode':
        '''FESubstructureNode: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2126.FESubstructureNode)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2126.FESubstructureNode]':
        '''List[FESubstructureNode]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2126.FESubstructureNode))
        return value


class ListWithSelectedItem_Datum(_2190.Datum, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_Datum

    A specific implementation of 'ListWithSelectedItem' for 'Datum' types.
    '''

    __hash__ = None
    __qualname__ = 'Datum'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_Datum.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2190.Datum.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2190.Datum.TYPE

    @property
    def selected_value(self) -> '_2190.Datum':
        '''Datum: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2190.Datum)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2190.Datum]':
        '''List[Datum]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2190.Datum))
        return value


class ListWithSelectedItem_Component(_2186.Component, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_Component

    A specific implementation of 'ListWithSelectedItem' for 'Component' types.
    '''

    __hash__ = None
    __qualname__ = 'Component'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_Component.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2186.Component.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2186.Component.TYPE

    @property
    def selected_value(self) -> '_2186.Component':
        '''Component: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2186.Component.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Component. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AbstractShaft. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_abstract_shaft_or_housing(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AbstractShaftOrHousing. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Bearing. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bolt(self) -> '_2184.Bolt':
        '''Bolt: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2184.Bolt.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Bolt. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_connector(self) -> '_2189.Connector':
        '''Connector: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Connector. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_datum(self) -> '_2190.Datum':
        '''Datum: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2190.Datum.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Datum. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_external_cad_model(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2193.ExternalCADModel.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ExternalCADModel. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FEPart. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_guide_dxf_model(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2196.GuideDxfModel.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GuideDxfModel. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_mass_disc(self) -> '_2203.MassDisc':
        '''MassDisc: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2203.MassDisc.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MassDisc. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_measurement_component(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2204.MeasurementComponent.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MeasurementComponent. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_mountable_component(self) -> '_2205.MountableComponent':
        '''MountableComponent: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2205.MountableComponent.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MountableComponent. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to OilSeal. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_planet_carrier(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2210.PlanetCarrier.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PlanetCarrier. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_point_load(self) -> '_2212.PointLoad':
        '''PointLoad: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2212.PointLoad.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PointLoad. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_power_load(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2213.PowerLoad.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PowerLoad. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_unbalanced_mass(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2218.UnbalancedMass.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to UnbalancedMass. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_virtual_component(self) -> '_2220.VirtualComponent':
        '''VirtualComponent: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2220.VirtualComponent.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to VirtualComponent. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Shaft. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_agma_gleason_conical_gear(self) -> '_2253.AGMAGleasonConicalGear':
        '''AGMAGleasonConicalGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2253.AGMAGleasonConicalGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AGMAGleasonConicalGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_differential_gear(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelDifferentialGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_differential_planet_gear(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2257.BevelDifferentialPlanetGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelDifferentialPlanetGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_differential_sun_gear(self) -> '_2258.BevelDifferentialSunGear':
        '''BevelDifferentialSunGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2258.BevelDifferentialSunGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelDifferentialSunGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_gear(self) -> '_2259.BevelGear':
        '''BevelGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2259.BevelGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_concept_gear(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2261.ConceptGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConceptGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_conical_gear(self) -> '_2263.ConicalGear':
        '''ConicalGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2263.ConicalGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConicalGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_planet_gear(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2267.CylindricalPlanetGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalPlanetGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_face_gear(self) -> '_2268.FaceGear':
        '''FaceGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2268.FaceGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FaceGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear(self) -> '_2270.Gear':
        '''Gear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2270.Gear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Gear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_hypoid_gear(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2274.HypoidGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HypoidGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_conical_gear(self) -> '_2276.KlingelnbergCycloPalloidConicalGear':
        '''KlingelnbergCycloPalloidConicalGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2276.KlingelnbergCycloPalloidConicalGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidConicalGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_hypoid_gear(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2278.KlingelnbergCycloPalloidHypoidGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidHypoidGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2280.KlingelnbergCycloPalloidSpiralBevelGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidSpiralBevelGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_spiral_bevel_gear(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2283.SpiralBevelGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpiralBevelGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_diff_gear(self) -> '_2285.StraightBevelDiffGear':
        '''StraightBevelDiffGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2285.StraightBevelDiffGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelDiffGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_gear(self) -> '_2287.StraightBevelGear':
        '''StraightBevelGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2287.StraightBevelGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_planet_gear(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2289.StraightBevelPlanetGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelPlanetGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_sun_gear(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2290.StraightBevelSunGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelSunGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_worm_gear(self) -> '_2291.WormGear':
        '''WormGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2291.WormGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to WormGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_zerol_bevel_gear(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2293.ZerolBevelGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ZerolBevelGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CycloidalDisc. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_ring_pins(self) -> '_2310.RingPins':
        '''RingPins: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2310.RingPins.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to RingPins. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_clutch_half(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2319.ClutchHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ClutchHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_concept_coupling_half(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2322.ConceptCouplingHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConceptCouplingHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_coupling_half(self) -> '_2324.CouplingHalf':
        '''CouplingHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2324.CouplingHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CouplingHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cvt_pulley(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2327.CVTPulley.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CVTPulley. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_part_to_part_shear_coupling_half(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2329.PartToPartShearCouplingHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PartToPartShearCouplingHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_pulley(self) -> '_2330.Pulley':
        '''Pulley: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to Pulley. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_rolling_ring(self) -> '_2336.RollingRing':
        '''RollingRing: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2336.RollingRing.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to RollingRing. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ShaftHubConnection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_spring_damper_half(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2341.SpringDamperHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpringDamperHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_synchroniser_half(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2344.SynchroniserHalf.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SynchroniserHalf. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_synchroniser_part(self) -> '_2345.SynchroniserPart':
        '''SynchroniserPart: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2345.SynchroniserPart.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SynchroniserPart. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_synchroniser_sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2346.SynchroniserSleeve.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SynchroniserSleeve. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque_converter_pump(self) -> '_2348.TorqueConverterPump':
        '''TorqueConverterPump: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2348.TorqueConverterPump.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TorqueConverterPump. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_torque_converter_turbine(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2350.TorqueConverterTurbine.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to TorqueConverterTurbine. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2186.Component]':
        '''List[Component]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2186.Component))
        return value


class ListWithSelectedItem_FELink(_2159.FELink, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_FELink

    A specific implementation of 'ListWithSelectedItem' for 'FELink' types.
    '''

    __hash__ = None
    __qualname__ = 'FELink'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_FELink.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2159.FELink.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2159.FELink.TYPE

    @property
    def selected_value(self) -> '_2159.FELink':
        '''FELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2159.FELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_electric_machine_stator_fe_link(self) -> '_2160.ElectricMachineStatorFELink':
        '''ElectricMachineStatorFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2160.ElectricMachineStatorFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ElectricMachineStatorFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear_mesh_fe_link(self) -> '_2162.GearMeshFELink':
        '''GearMeshFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2162.GearMeshFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearMeshFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_gear_with_duplicated_meshes_fe_link(self) -> '_2163.GearWithDuplicatedMeshesFELink':
        '''GearWithDuplicatedMeshesFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2163.GearWithDuplicatedMeshesFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearWithDuplicatedMeshesFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_multi_angle_connection_fe_link(self) -> '_2164.MultiAngleConnectionFELink':
        '''MultiAngleConnectionFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2164.MultiAngleConnectionFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MultiAngleConnectionFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_multi_node_connector_fe_link(self) -> '_2165.MultiNodeConnectorFELink':
        '''MultiNodeConnectorFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2165.MultiNodeConnectorFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MultiNodeConnectorFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_multi_node_fe_link(self) -> '_2166.MultiNodeFELink':
        '''MultiNodeFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2166.MultiNodeFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to MultiNodeFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_planetary_connector_multi_node_fe_link(self) -> '_2167.PlanetaryConnectorMultiNodeFELink':
        '''PlanetaryConnectorMultiNodeFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2167.PlanetaryConnectorMultiNodeFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PlanetaryConnectorMultiNodeFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_planet_based_fe_link(self) -> '_2168.PlanetBasedFELink':
        '''PlanetBasedFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2168.PlanetBasedFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PlanetBasedFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_planet_carrier_fe_link(self) -> '_2169.PlanetCarrierFELink':
        '''PlanetCarrierFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2169.PlanetCarrierFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PlanetCarrierFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_point_load_fe_link(self) -> '_2170.PointLoadFELink':
        '''PointLoadFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2170.PointLoadFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to PointLoadFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_rolling_ring_connection_fe_link(self) -> '_2171.RollingRingConnectionFELink':
        '''RollingRingConnectionFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2171.RollingRingConnectionFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to RollingRingConnectionFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_shaft_hub_connection_fe_link(self) -> '_2172.ShaftHubConnectionFELink':
        '''ShaftHubConnectionFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2172.ShaftHubConnectionFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ShaftHubConnectionFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_single_node_fe_link(self) -> '_2173.SingleNodeFELink':
        '''SingleNodeFELink: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2173.SingleNodeFELink.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SingleNodeFELink. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2159.FELink]':
        '''List[FELink]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2159.FELink))
        return value


class ListWithSelectedItem_FESubstructure(_2124.FESubstructure, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_FESubstructure

    A specific implementation of 'ListWithSelectedItem' for 'FESubstructure' types.
    '''

    __hash__ = None
    __qualname__ = 'FESubstructure'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_FESubstructure.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2124.FESubstructure.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2124.FESubstructure.TYPE

    @property
    def selected_value(self) -> '_2124.FESubstructure':
        '''FESubstructure: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2124.FESubstructure)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2124.FESubstructure]':
        '''List[FESubstructure]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2124.FESubstructure))
        return value


class ListWithSelectedItem_CylindricalGear(_2265.CylindricalGear, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalGear

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalGear' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGear'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalGear.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2265.CylindricalGear.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2265.CylindricalGear.TYPE

    @property
    def selected_value(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGear. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2265.CylindricalGear]':
        '''List[CylindricalGear]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2265.CylindricalGear))
        return value


class ListWithSelectedItem_GuideDxfModel(_2196.GuideDxfModel, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_GuideDxfModel

    A specific implementation of 'ListWithSelectedItem' for 'GuideDxfModel' types.
    '''

    __hash__ = None
    __qualname__ = 'GuideDxfModel'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_GuideDxfModel.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2196.GuideDxfModel.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2196.GuideDxfModel.TYPE

    @property
    def selected_value(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2196.GuideDxfModel)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2196.GuideDxfModel]':
        '''List[GuideDxfModel]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2196.GuideDxfModel))
        return value


class ListWithSelectedItem_ConcentricPartGroup(_2228.ConcentricPartGroup, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ConcentricPartGroup

    A specific implementation of 'ListWithSelectedItem' for 'ConcentricPartGroup' types.
    '''

    __hash__ = None
    __qualname__ = 'ConcentricPartGroup'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ConcentricPartGroup.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2228.ConcentricPartGroup.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2228.ConcentricPartGroup.TYPE

    @property
    def selected_value(self) -> '_2228.ConcentricPartGroup':
        '''ConcentricPartGroup: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2228.ConcentricPartGroup)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2228.ConcentricPartGroup]':
        '''List[ConcentricPartGroup]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2228.ConcentricPartGroup))
        return value


class ListWithSelectedItem_CylindricalGearSet(_2266.CylindricalGearSet, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalGearSet

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalGearSet' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGearSet'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalGearSet.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2266.CylindricalGearSet.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2266.CylindricalGearSet.TYPE

    @property
    def selected_value(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSet. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2266.CylindricalGearSet]':
        '''List[CylindricalGearSet]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2266.CylindricalGearSet))
        return value


class ListWithSelectedItem_GearSetDesign(_907.GearSetDesign, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_GearSetDesign

    A specific implementation of 'ListWithSelectedItem' for 'GearSetDesign' types.
    '''

    __hash__ = None
    __qualname__ = 'GearSetDesign'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_GearSetDesign.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_907.GearSetDesign.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _907.GearSetDesign.TYPE

    @property
    def selected_value(self) -> '_907.GearSetDesign':
        '''GearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _907.GearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to GearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_zerol_bevel_gear_set_design(self) -> '_911.ZerolBevelGearSetDesign':
        '''ZerolBevelGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _911.ZerolBevelGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ZerolBevelGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_worm_gear_set_design(self) -> '_916.WormGearSetDesign':
        '''WormGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _916.WormGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to WormGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_diff_gear_set_design(self) -> '_920.StraightBevelDiffGearSetDesign':
        '''StraightBevelDiffGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _920.StraightBevelDiffGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelDiffGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_straight_bevel_gear_set_design(self) -> '_924.StraightBevelGearSetDesign':
        '''StraightBevelGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _924.StraightBevelGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StraightBevelGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_spiral_bevel_gear_set_design(self) -> '_928.SpiralBevelGearSetDesign':
        '''SpiralBevelGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _928.SpiralBevelGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to SpiralBevelGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_design(self) -> '_932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidSpiralBevelGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_design(self) -> '_936.KlingelnbergCycloPalloidHypoidGearSetDesign':
        '''KlingelnbergCycloPalloidHypoidGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _936.KlingelnbergCycloPalloidHypoidGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergCycloPalloidHypoidGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_klingelnberg_conical_gear_set_design(self) -> '_940.KlingelnbergConicalGearSetDesign':
        '''KlingelnbergConicalGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _940.KlingelnbergConicalGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to KlingelnbergConicalGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_hypoid_gear_set_design(self) -> '_944.HypoidGearSetDesign':
        '''HypoidGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _944.HypoidGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to HypoidGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_face_gear_set_design(self) -> '_952.FaceGearSetDesign':
        '''FaceGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _952.FaceGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to FaceGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_planetary_gear_set_design(self) -> '_995.CylindricalPlanetaryGearSetDesign':
        '''CylindricalPlanetaryGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _995.CylindricalPlanetaryGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalPlanetaryGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_conical_gear_set_design(self) -> '_1103.ConicalGearSetDesign':
        '''ConicalGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1103.ConicalGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConicalGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_concept_gear_set_design(self) -> '_1125.ConceptGearSetDesign':
        '''ConceptGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1125.ConceptGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to ConceptGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_bevel_gear_set_design(self) -> '_1129.BevelGearSetDesign':
        '''BevelGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1129.BevelGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to BevelGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_agma_gleason_conical_gear_set_design(self) -> '_1142.AGMAGleasonConicalGearSetDesign':
        '''AGMAGleasonConicalGearSetDesign: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1142.AGMAGleasonConicalGearSetDesign.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to AGMAGleasonConicalGearSetDesign. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_907.GearSetDesign]':
        '''List[GearSetDesign]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_907.GearSetDesign))
        return value


class ListWithSelectedItem_ShaftHubConnection(_2338.ShaftHubConnection, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ShaftHubConnection

    A specific implementation of 'ListWithSelectedItem' for 'ShaftHubConnection' types.
    '''

    __hash__ = None
    __qualname__ = 'ShaftHubConnection'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ShaftHubConnection.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2338.ShaftHubConnection.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2338.ShaftHubConnection.TYPE

    @property
    def selected_value(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2338.ShaftHubConnection)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2338.ShaftHubConnection]':
        '''List[ShaftHubConnection]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2338.ShaftHubConnection))
        return value


class ListWithSelectedItem_TSelectableItem(Generic[TSelectableItem], mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_TSelectableItem

    A specific implementation of 'ListWithSelectedItem' for 'TSelectableItem' types.
    '''

    __hash__ = None
    __qualname__ = 'TSelectableItem'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_TSelectableItem.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'TSelectableItem':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return TSelectableItem

    @property
    def selected_value(self) -> 'TSelectableItem':
        '''TSelectableItem: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[TSelectableItem]':
        '''List[TSelectableItem]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues)
        return value


class ListWithSelectedItem_CylindricalGearSystemDeflection(_2480.CylindricalGearSystemDeflection, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_CylindricalGearSystemDeflection

    A specific implementation of 'ListWithSelectedItem' for 'CylindricalGearSystemDeflection' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGearSystemDeflection'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_CylindricalGearSystemDeflection.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2480.CylindricalGearSystemDeflection.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2480.CylindricalGearSystemDeflection.TYPE

    @property
    def selected_value(self) -> '_2480.CylindricalGearSystemDeflection':
        '''CylindricalGearSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2480.CylindricalGearSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_system_deflection_timestep(self) -> '_2481.CylindricalGearSystemDeflectionTimestep':
        '''CylindricalGearSystemDeflectionTimestep: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2481.CylindricalGearSystemDeflectionTimestep.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSystemDeflectionTimestep. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_gear_system_deflection_with_ltca_results(self) -> '_2482.CylindricalGearSystemDeflectionWithLTCAResults':
        '''CylindricalGearSystemDeflectionWithLTCAResults: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2482.CylindricalGearSystemDeflectionWithLTCAResults.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalGearSystemDeflectionWithLTCAResults. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def selected_value_of_type_cylindrical_planet_gear_system_deflection(self) -> '_2485.CylindricalPlanetGearSystemDeflection':
        '''CylindricalPlanetGearSystemDeflection: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2485.CylindricalPlanetGearSystemDeflection.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to CylindricalPlanetGearSystemDeflection. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2480.CylindricalGearSystemDeflection]':
        '''List[CylindricalGearSystemDeflection]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2480.CylindricalGearSystemDeflection))
        return value


class ListWithSelectedItem_DesignState(_5388.DesignState, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_DesignState

    A specific implementation of 'ListWithSelectedItem' for 'DesignState' types.
    '''

    __hash__ = None
    __qualname__ = 'DesignState'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_DesignState.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_5388.DesignState.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _5388.DesignState.TYPE

    @property
    def selected_value(self) -> '_5388.DesignState':
        '''DesignState: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5388.DesignState)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_5388.DesignState]':
        '''List[DesignState]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_5388.DesignState))
        return value


class ListWithSelectedItem_FEPart(_2194.FEPart, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_FEPart

    A specific implementation of 'ListWithSelectedItem' for 'FEPart' types.
    '''

    __hash__ = None
    __qualname__ = 'FEPart'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_FEPart.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2194.FEPart.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2194.FEPart.TYPE

    @property
    def selected_value(self) -> '_2194.FEPart':
        '''FEPart: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2194.FEPart]':
        '''List[FEPart]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2194.FEPart))
        return value


class ListWithSelectedItem_TPartAnalysis(Generic[TPartAnalysis], mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_TPartAnalysis

    A specific implementation of 'ListWithSelectedItem' for 'TPartAnalysis' types.
    '''

    __hash__ = None
    __qualname__ = 'TPartAnalysis'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_TPartAnalysis.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'TPartAnalysis':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return TPartAnalysis

    @property
    def selected_value(self) -> 'TPartAnalysis':
        '''TPartAnalysis: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[TPartAnalysis]':
        '''List[TPartAnalysis]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues)
        return value


class ListWithSelectedItem_ResultLocationSelectionGroup(_5827.ResultLocationSelectionGroup, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ResultLocationSelectionGroup

    A specific implementation of 'ListWithSelectedItem' for 'ResultLocationSelectionGroup' types.
    '''

    __hash__ = None
    __qualname__ = 'ResultLocationSelectionGroup'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ResultLocationSelectionGroup.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_5827.ResultLocationSelectionGroup.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _5827.ResultLocationSelectionGroup.TYPE

    @property
    def selected_value(self) -> '_5827.ResultLocationSelectionGroup':
        '''ResultLocationSelectionGroup: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5827.ResultLocationSelectionGroup)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_5827.ResultLocationSelectionGroup]':
        '''List[ResultLocationSelectionGroup]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_5827.ResultLocationSelectionGroup))
        return value


class ListWithSelectedItem_StaticLoadCase(_6519.StaticLoadCase, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_StaticLoadCase

    A specific implementation of 'ListWithSelectedItem' for 'StaticLoadCase' types.
    '''

    __hash__ = None
    __qualname__ = 'StaticLoadCase'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_StaticLoadCase.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_6519.StaticLoadCase.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _6519.StaticLoadCase.TYPE

    @property
    def selected_value(self) -> '_6519.StaticLoadCase':
        '''StaticLoadCase: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6519.StaticLoadCase.TYPE not in self.enclosing.SelectedValue.__class__.__mro__:
            raise CastException('Failed to cast selected_value to StaticLoadCase. Expected: {}.'.format(self.enclosing.SelectedValue.__class__.__qualname__))

        return constructor.new_override(self.enclosing.SelectedValue.__class__)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_6519.StaticLoadCase]':
        '''List[StaticLoadCase]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_6519.StaticLoadCase))
        return value


class ListWithSelectedItem_DutyCycle(_5389.DutyCycle, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_DutyCycle

    A specific implementation of 'ListWithSelectedItem' for 'DutyCycle' types.
    '''

    __hash__ = None
    __qualname__ = 'DutyCycle'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_DutyCycle.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_5389.DutyCycle.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _5389.DutyCycle.TYPE

    @property
    def selected_value(self) -> '_5389.DutyCycle':
        '''DutyCycle: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5389.DutyCycle)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_5389.DutyCycle]':
        '''List[DutyCycle]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_5389.DutyCycle))
        return value


class ListWithSelectedItem_float(float, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_float

    A specific implementation of 'ListWithSelectedItem' for 'float' types.
    '''

    __hash__ = None
    __qualname__ = 'float'

    def __new__(cls, instance_to_wrap: 'ListWithSelectedItem_float.TYPE'):
        return float.__new__(cls, instance_to_wrap.SelectedValue if instance_to_wrap.SelectedValue is not None else 0.0)

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_float.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.SelectedValue
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> 'float':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return float

    @property
    def selected_value(self) -> 'float':
        '''float: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.SelectedValue

    @property
    def available_values(self) -> 'List[float]':
        '''List[float]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.enclosing.AvailableValues)
        return value


class ListWithSelectedItem_ElectricMachineDataSet(_2115.ElectricMachineDataSet, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_ElectricMachineDataSet

    A specific implementation of 'ListWithSelectedItem' for 'ElectricMachineDataSet' types.
    '''

    __hash__ = None
    __qualname__ = 'ElectricMachineDataSet'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_ElectricMachineDataSet.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2115.ElectricMachineDataSet.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2115.ElectricMachineDataSet.TYPE

    @property
    def selected_value(self) -> '_2115.ElectricMachineDataSet':
        '''ElectricMachineDataSet: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2115.ElectricMachineDataSet)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2115.ElectricMachineDataSet]':
        '''List[ElectricMachineDataSet]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2115.ElectricMachineDataSet))
        return value


class ListWithSelectedItem_PointLoad(_2212.PointLoad, mixins.ListWithSelectedItemMixin):
    '''ListWithSelectedItem_PointLoad

    A specific implementation of 'ListWithSelectedItem' for 'PointLoad' types.
    '''

    __hash__ = None
    __qualname__ = 'PointLoad'

    def __init__(self, instance_to_wrap: 'ListWithSelectedItem_PointLoad.TYPE'):
        try:
            self.enclosing = instance_to_wrap
        except (TypeError, AttributeError):
            pass
        super().__init__(instance_to_wrap.SelectedValue)

    @classmethod
    def wrapper_type(cls) -> '_LIST_WITH_SELECTED_ITEM':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _LIST_WITH_SELECTED_ITEM

    @classmethod
    def implicit_type(cls) -> '_2212.PointLoad.TYPE':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2212.PointLoad.TYPE

    @property
    def selected_value(self) -> '_2212.PointLoad':
        '''PointLoad: 'SelectedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.enclosing.SelectedValue) if self.enclosing.SelectedValue is not None else None

    @property
    def available_values(self) -> 'List[_2212.PointLoad]':
        '''List[PointLoad]: 'AvailableValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.enclosing.AvailableValues, constructor.new(_2212.PointLoad))
        return value
