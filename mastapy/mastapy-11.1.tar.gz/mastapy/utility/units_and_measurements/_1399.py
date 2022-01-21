'''_1399.py

MeasurementSettings
'''


from mastapy._internal.implicit import list_with_selected_item, overridable
from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
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
from mastapy._internal.cast_exception import CastException
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_SETTINGS = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'MeasurementSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementSettings',)


class MeasurementSettings(_1387.PerMachineSettings):
    '''MeasurementSettings

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def selected_measurement(self) -> 'list_with_selected_item.ListWithSelectedItem_MeasurementBase':
        '''list_with_selected_item.ListWithSelectedItem_MeasurementBase: 'SelectedMeasurement' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_MeasurementBase)(self.wrapped.SelectedMeasurement) if self.wrapped.SelectedMeasurement is not None else None

    @selected_measurement.setter
    def selected_measurement(self, value: 'list_with_selected_item.ListWithSelectedItem_MeasurementBase.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_MeasurementBase.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_MeasurementBase.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SelectedMeasurement = value

    @property
    def sample_input(self) -> 'str':
        '''str: 'SampleInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SampleInput

    @property
    def sample_output(self) -> 'str':
        '''str: 'SampleOutput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SampleOutput

    @property
    def number_decimal_separator(self) -> 'str':
        '''str: 'NumberDecimalSeparator' is the original name of this property.'''

        return self.wrapped.NumberDecimalSeparator

    @number_decimal_separator.setter
    def number_decimal_separator(self, value: 'str'):
        self.wrapped.NumberDecimalSeparator = str(value) if value else ''

    @property
    def number_group_separator(self) -> 'str':
        '''str: 'NumberGroupSeparator' is the original name of this property.'''

        return self.wrapped.NumberGroupSeparator

    @number_group_separator.setter
    def number_group_separator(self, value: 'str'):
        self.wrapped.NumberGroupSeparator = str(value) if value else ''

    @property
    def small_number_cutoff(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SmallNumberCutoff' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SmallNumberCutoff) if self.wrapped.SmallNumberCutoff is not None else None

    @small_number_cutoff.setter
    def small_number_cutoff(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SmallNumberCutoff = value

    @property
    def large_number_cutoff(self) -> 'float':
        '''float: 'LargeNumberCutoff' is the original name of this property.'''

        return self.wrapped.LargeNumberCutoff

    @large_number_cutoff.setter
    def large_number_cutoff(self, value: 'float'):
        self.wrapped.LargeNumberCutoff = float(value) if value else 0.0

    @property
    def show_trailing_zeros(self) -> 'bool':
        '''bool: 'ShowTrailingZeros' is the original name of this property.'''

        return self.wrapped.ShowTrailingZeros

    @show_trailing_zeros.setter
    def show_trailing_zeros(self, value: 'bool'):
        self.wrapped.ShowTrailingZeros = bool(value) if value else False

    @property
    def current_selected_measurement(self) -> '_1398.MeasurementBase':
        '''MeasurementBase: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1398.MeasurementBase.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MeasurementBase. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_acceleration(self) -> '_1405.Acceleration':
        '''Acceleration: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1405.Acceleration.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Acceleration. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angle(self) -> '_1406.Angle':
        '''Angle: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1406.Angle.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Angle. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angle_per_unit_temperature(self) -> '_1407.AnglePerUnitTemperature':
        '''AnglePerUnitTemperature: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1407.AnglePerUnitTemperature.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AnglePerUnitTemperature. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angle_small(self) -> '_1408.AngleSmall':
        '''AngleSmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1408.AngleSmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngleSmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angle_very_small(self) -> '_1409.AngleVerySmall':
        '''AngleVerySmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1409.AngleVerySmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngleVerySmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angular_acceleration(self) -> '_1410.AngularAcceleration':
        '''AngularAcceleration: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1410.AngularAcceleration.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngularAcceleration. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angular_compliance(self) -> '_1411.AngularCompliance':
        '''AngularCompliance: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1411.AngularCompliance.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngularCompliance. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angular_jerk(self) -> '_1412.AngularJerk':
        '''AngularJerk: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1412.AngularJerk.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngularJerk. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angular_stiffness(self) -> '_1413.AngularStiffness':
        '''AngularStiffness: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1413.AngularStiffness.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngularStiffness. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_angular_velocity(self) -> '_1414.AngularVelocity':
        '''AngularVelocity: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1414.AngularVelocity.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AngularVelocity. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_area(self) -> '_1415.Area':
        '''Area: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1415.Area.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Area. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_area_small(self) -> '_1416.AreaSmall':
        '''AreaSmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1416.AreaSmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to AreaSmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_cycles(self) -> '_1417.Cycles':
        '''Cycles: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1417.Cycles.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Cycles. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_damage(self) -> '_1418.Damage':
        '''Damage: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1418.Damage.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Damage. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_damage_rate(self) -> '_1419.DamageRate':
        '''DamageRate: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1419.DamageRate.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to DamageRate. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_data_size(self) -> '_1420.DataSize':
        '''DataSize: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1420.DataSize.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to DataSize. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_decibel(self) -> '_1421.Decibel':
        '''Decibel: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1421.Decibel.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Decibel. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_density(self) -> '_1422.Density':
        '''Density: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1422.Density.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Density. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_energy(self) -> '_1423.Energy':
        '''Energy: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1423.Energy.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Energy. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_energy_per_unit_area(self) -> '_1424.EnergyPerUnitArea':
        '''EnergyPerUnitArea: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1424.EnergyPerUnitArea.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to EnergyPerUnitArea. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_energy_per_unit_area_small(self) -> '_1425.EnergyPerUnitAreaSmall':
        '''EnergyPerUnitAreaSmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1425.EnergyPerUnitAreaSmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to EnergyPerUnitAreaSmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_energy_small(self) -> '_1426.EnergySmall':
        '''EnergySmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1426.EnergySmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to EnergySmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_enum(self) -> '_1427.Enum':
        '''Enum: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1427.Enum.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Enum. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_flow_rate(self) -> '_1428.FlowRate':
        '''FlowRate: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1428.FlowRate.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to FlowRate. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_force(self) -> '_1429.Force':
        '''Force: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1429.Force.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Force. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_force_per_unit_length(self) -> '_1430.ForcePerUnitLength':
        '''ForcePerUnitLength: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1430.ForcePerUnitLength.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ForcePerUnitLength. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_force_per_unit_pressure(self) -> '_1431.ForcePerUnitPressure':
        '''ForcePerUnitPressure: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1431.ForcePerUnitPressure.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ForcePerUnitPressure. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_force_per_unit_temperature(self) -> '_1432.ForcePerUnitTemperature':
        '''ForcePerUnitTemperature: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1432.ForcePerUnitTemperature.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ForcePerUnitTemperature. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_fraction_measurement_base(self) -> '_1433.FractionMeasurementBase':
        '''FractionMeasurementBase: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1433.FractionMeasurementBase.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to FractionMeasurementBase. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_frequency(self) -> '_1434.Frequency':
        '''Frequency: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1434.Frequency.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Frequency. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_fuel_consumption_engine(self) -> '_1435.FuelConsumptionEngine':
        '''FuelConsumptionEngine: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1435.FuelConsumptionEngine.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to FuelConsumptionEngine. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_fuel_efficiency_vehicle(self) -> '_1436.FuelEfficiencyVehicle':
        '''FuelEfficiencyVehicle: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1436.FuelEfficiencyVehicle.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to FuelEfficiencyVehicle. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_gradient(self) -> '_1437.Gradient':
        '''Gradient: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1437.Gradient.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Gradient. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_heat_conductivity(self) -> '_1438.HeatConductivity':
        '''HeatConductivity: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1438.HeatConductivity.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to HeatConductivity. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_heat_transfer(self) -> '_1439.HeatTransfer':
        '''HeatTransfer: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1439.HeatTransfer.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to HeatTransfer. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_heat_transfer_coefficient_for_plastic_gear_tooth(self) -> '_1440.HeatTransferCoefficientForPlasticGearTooth':
        '''HeatTransferCoefficientForPlasticGearTooth: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1440.HeatTransferCoefficientForPlasticGearTooth.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to HeatTransferCoefficientForPlasticGearTooth. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_heat_transfer_resistance(self) -> '_1441.HeatTransferResistance':
        '''HeatTransferResistance: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1441.HeatTransferResistance.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to HeatTransferResistance. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_impulse(self) -> '_1442.Impulse':
        '''Impulse: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1442.Impulse.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Impulse. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_index(self) -> '_1443.Index':
        '''Index: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1443.Index.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Index. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_integer(self) -> '_1444.Integer':
        '''Integer: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1444.Integer.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Integer. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_inverse_short_length(self) -> '_1445.InverseShortLength':
        '''InverseShortLength: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1445.InverseShortLength.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to InverseShortLength. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_inverse_short_time(self) -> '_1446.InverseShortTime':
        '''InverseShortTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1446.InverseShortTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to InverseShortTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_jerk(self) -> '_1447.Jerk':
        '''Jerk: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1447.Jerk.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Jerk. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_kinematic_viscosity(self) -> '_1448.KinematicViscosity':
        '''KinematicViscosity: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1448.KinematicViscosity.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to KinematicViscosity. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_long(self) -> '_1449.LengthLong':
        '''LengthLong: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1449.LengthLong.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthLong. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_medium(self) -> '_1450.LengthMedium':
        '''LengthMedium: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1450.LengthMedium.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthMedium. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_per_unit_temperature(self) -> '_1451.LengthPerUnitTemperature':
        '''LengthPerUnitTemperature: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1451.LengthPerUnitTemperature.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthPerUnitTemperature. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_short(self) -> '_1452.LengthShort':
        '''LengthShort: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1452.LengthShort.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthShort. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_to_the_fourth(self) -> '_1453.LengthToTheFourth':
        '''LengthToTheFourth: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1453.LengthToTheFourth.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthToTheFourth. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_very_long(self) -> '_1454.LengthVeryLong':
        '''LengthVeryLong: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1454.LengthVeryLong.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthVeryLong. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_very_short(self) -> '_1455.LengthVeryShort':
        '''LengthVeryShort: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1455.LengthVeryShort.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthVeryShort. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_length_very_short_per_length_short(self) -> '_1456.LengthVeryShortPerLengthShort':
        '''LengthVeryShortPerLengthShort: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1456.LengthVeryShortPerLengthShort.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LengthVeryShortPerLengthShort. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_linear_angular_damping(self) -> '_1457.LinearAngularDamping':
        '''LinearAngularDamping: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1457.LinearAngularDamping.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LinearAngularDamping. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_linear_angular_stiffness_cross_term(self) -> '_1458.LinearAngularStiffnessCrossTerm':
        '''LinearAngularStiffnessCrossTerm: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1458.LinearAngularStiffnessCrossTerm.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LinearAngularStiffnessCrossTerm. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_linear_damping(self) -> '_1459.LinearDamping':
        '''LinearDamping: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1459.LinearDamping.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LinearDamping. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_linear_flexibility(self) -> '_1460.LinearFlexibility':
        '''LinearFlexibility: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1460.LinearFlexibility.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LinearFlexibility. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_linear_stiffness(self) -> '_1461.LinearStiffness':
        '''LinearStiffness: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1461.LinearStiffness.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to LinearStiffness. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_mass(self) -> '_1462.Mass':
        '''Mass: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1462.Mass.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Mass. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_mass_per_unit_length(self) -> '_1463.MassPerUnitLength':
        '''MassPerUnitLength: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1463.MassPerUnitLength.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MassPerUnitLength. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_mass_per_unit_time(self) -> '_1464.MassPerUnitTime':
        '''MassPerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1464.MassPerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MassPerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_moment_of_inertia(self) -> '_1465.MomentOfInertia':
        '''MomentOfInertia: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1465.MomentOfInertia.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MomentOfInertia. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_moment_of_inertia_per_unit_length(self) -> '_1466.MomentOfInertiaPerUnitLength':
        '''MomentOfInertiaPerUnitLength: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1466.MomentOfInertiaPerUnitLength.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MomentOfInertiaPerUnitLength. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_moment_per_unit_pressure(self) -> '_1467.MomentPerUnitPressure':
        '''MomentPerUnitPressure: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1467.MomentPerUnitPressure.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to MomentPerUnitPressure. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_number(self) -> '_1468.Number':
        '''Number: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1468.Number.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Number. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_percentage(self) -> '_1469.Percentage':
        '''Percentage: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1469.Percentage.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Percentage. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power(self) -> '_1470.Power':
        '''Power: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1470.Power.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Power. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_per_small_area(self) -> '_1471.PowerPerSmallArea':
        '''PowerPerSmallArea: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1471.PowerPerSmallArea.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerPerSmallArea. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_per_unit_time(self) -> '_1472.PowerPerUnitTime':
        '''PowerPerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1472.PowerPerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerPerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_small(self) -> '_1473.PowerSmall':
        '''PowerSmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1473.PowerSmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerSmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_small_per_area(self) -> '_1474.PowerSmallPerArea':
        '''PowerSmallPerArea: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1474.PowerSmallPerArea.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerSmallPerArea. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_small_per_unit_area_per_unit_time(self) -> '_1475.PowerSmallPerUnitAreaPerUnitTime':
        '''PowerSmallPerUnitAreaPerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1475.PowerSmallPerUnitAreaPerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerSmallPerUnitAreaPerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_power_small_per_unit_time(self) -> '_1476.PowerSmallPerUnitTime':
        '''PowerSmallPerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1476.PowerSmallPerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PowerSmallPerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_pressure(self) -> '_1477.Pressure':
        '''Pressure: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1477.Pressure.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Pressure. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_pressure_per_unit_time(self) -> '_1478.PressurePerUnitTime':
        '''PressurePerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1478.PressurePerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PressurePerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_pressure_velocity_product(self) -> '_1479.PressureVelocityProduct':
        '''PressureVelocityProduct: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1479.PressureVelocityProduct.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PressureVelocityProduct. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_pressure_viscosity_coefficient(self) -> '_1480.PressureViscosityCoefficient':
        '''PressureViscosityCoefficient: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1480.PressureViscosityCoefficient.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to PressureViscosityCoefficient. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_price(self) -> '_1481.Price':
        '''Price: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1481.Price.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Price. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_quadratic_angular_damping(self) -> '_1482.QuadraticAngularDamping':
        '''QuadraticAngularDamping: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1482.QuadraticAngularDamping.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to QuadraticAngularDamping. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_quadratic_drag(self) -> '_1483.QuadraticDrag':
        '''QuadraticDrag: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1483.QuadraticDrag.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to QuadraticDrag. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_rescaled_measurement(self) -> '_1484.RescaledMeasurement':
        '''RescaledMeasurement: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1484.RescaledMeasurement.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to RescaledMeasurement. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_rotatum(self) -> '_1485.Rotatum':
        '''Rotatum: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1485.Rotatum.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Rotatum. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_safety_factor(self) -> '_1486.SafetyFactor':
        '''SafetyFactor: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1486.SafetyFactor.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to SafetyFactor. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_specific_acoustic_impedance(self) -> '_1487.SpecificAcousticImpedance':
        '''SpecificAcousticImpedance: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1487.SpecificAcousticImpedance.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to SpecificAcousticImpedance. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_specific_heat(self) -> '_1488.SpecificHeat':
        '''SpecificHeat: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1488.SpecificHeat.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to SpecificHeat. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_square_root_of_unit_force_per_unit_area(self) -> '_1489.SquareRootOfUnitForcePerUnitArea':
        '''SquareRootOfUnitForcePerUnitArea: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1489.SquareRootOfUnitForcePerUnitArea.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to SquareRootOfUnitForcePerUnitArea. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_stiffness_per_unit_face_width(self) -> '_1490.StiffnessPerUnitFaceWidth':
        '''StiffnessPerUnitFaceWidth: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1490.StiffnessPerUnitFaceWidth.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to StiffnessPerUnitFaceWidth. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_stress(self) -> '_1491.Stress':
        '''Stress: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1491.Stress.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Stress. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_temperature(self) -> '_1492.Temperature':
        '''Temperature: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1492.Temperature.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Temperature. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_temperature_difference(self) -> '_1493.TemperatureDifference':
        '''TemperatureDifference: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1493.TemperatureDifference.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TemperatureDifference. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_temperature_per_unit_time(self) -> '_1494.TemperaturePerUnitTime':
        '''TemperaturePerUnitTime: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1494.TemperaturePerUnitTime.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TemperaturePerUnitTime. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_text(self) -> '_1495.Text':
        '''Text: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1495.Text.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Text. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_thermal_contact_coefficient(self) -> '_1496.ThermalContactCoefficient':
        '''ThermalContactCoefficient: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1496.ThermalContactCoefficient.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ThermalContactCoefficient. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_thermal_expansion_coefficient(self) -> '_1497.ThermalExpansionCoefficient':
        '''ThermalExpansionCoefficient: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1497.ThermalExpansionCoefficient.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ThermalExpansionCoefficient. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_thermo_elastic_factor(self) -> '_1498.ThermoElasticFactor':
        '''ThermoElasticFactor: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1498.ThermoElasticFactor.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to ThermoElasticFactor. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_time(self) -> '_1499.Time':
        '''Time: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1499.Time.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Time. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_time_short(self) -> '_1500.TimeShort':
        '''TimeShort: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1500.TimeShort.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TimeShort. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_time_very_short(self) -> '_1501.TimeVeryShort':
        '''TimeVeryShort: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1501.TimeVeryShort.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TimeVeryShort. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_torque(self) -> '_1502.Torque':
        '''Torque: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1502.Torque.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Torque. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_torque_converter_inverse_k(self) -> '_1503.TorqueConverterInverseK':
        '''TorqueConverterInverseK: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1503.TorqueConverterInverseK.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TorqueConverterInverseK. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_torque_converter_k(self) -> '_1504.TorqueConverterK':
        '''TorqueConverterK: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1504.TorqueConverterK.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TorqueConverterK. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_torque_per_unit_temperature(self) -> '_1505.TorquePerUnitTemperature':
        '''TorquePerUnitTemperature: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1505.TorquePerUnitTemperature.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to TorquePerUnitTemperature. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_velocity(self) -> '_1506.Velocity':
        '''Velocity: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1506.Velocity.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Velocity. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_velocity_small(self) -> '_1507.VelocitySmall':
        '''VelocitySmall: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1507.VelocitySmall.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to VelocitySmall. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_viscosity(self) -> '_1508.Viscosity':
        '''Viscosity: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1508.Viscosity.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Viscosity. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_voltage(self) -> '_1509.Voltage':
        '''Voltage: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1509.Voltage.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Voltage. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_volume(self) -> '_1510.Volume':
        '''Volume: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1510.Volume.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Volume. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_wear_coefficient(self) -> '_1511.WearCoefficient':
        '''WearCoefficient: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1511.WearCoefficient.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to WearCoefficient. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    @property
    def current_selected_measurement_of_type_yank(self) -> '_1512.Yank':
        '''Yank: 'CurrentSelectedMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1512.Yank.TYPE not in self.wrapped.CurrentSelectedMeasurement.__class__.__mro__:
            raise CastException('Failed to cast current_selected_measurement to Yank. Expected: {}.'.format(self.wrapped.CurrentSelectedMeasurement.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentSelectedMeasurement.__class__)(self.wrapped.CurrentSelectedMeasurement) if self.wrapped.CurrentSelectedMeasurement is not None else None

    def default_to_metric(self):
        ''' 'DefaultToMetric' is the original name of this method.'''

        self.wrapped.DefaultToMetric()

    def default_to_imperial(self):
        ''' 'DefaultToImperial' is the original name of this method.'''

        self.wrapped.DefaultToImperial()
