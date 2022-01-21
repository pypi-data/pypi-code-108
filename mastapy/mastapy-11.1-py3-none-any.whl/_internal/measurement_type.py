'''measurement_type.py

This module is essentially a copy of
mastapy.units_and_measurements.MeasurementType but without the additional
Python.NET type imports/references. The enum should be preferencially used
instead of a string in the masta_property decorator for the measurement
type.
'''

from enum import Enum


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementType',)


class MeasurementType(Enum):
    '''MeasurementType

    Enum of all of the acceptable measurement types for MASTA properties.
    '''

    __hash__ = None

    ALL = 0
    ACCELERATION = 1
    ANGLE = 2
    ANGULAR_STIFFNESS = 3
    ANGULAR_ACCELERATION = 4
    ANGULAR_VELOCITY = 5
    AREA = 6
    SMALL_AREA = 7
    CYCLES = 8
    DENSITY = 9
    ENERGY = 10
    ENERGY_PER_AREA = 11
    ENERGY_PER_SMALL_AREA = 12
    ELASTICITY_FACTOR = 13
    FLOW_RATE = 14
    FORCE = 15
    FORCE_PER_UNIT_LENGTH = 16
    FREQUENCY = 18
    FUEL_CONSUMPTION_PER_UNIT_ENERGY = 19
    FUEL_EFFICIENCY_PER_UNIT_DISTANCE = 20
    GRADIENT = 21
    HEAT_CONDUCTIVITY = 22
    IMPULSE = 23
    INERTIA = 24
    KINEMATIC_VISCOSITY = 25
    LINEAR_STIFFNESS = 27
    LINEAR_ANGULAR_STIFFNESS_CROSS_TERM = 28
    LONG_LENGTH = 29
    VERY_LONG_LENGTH = 30
    MASS = 31
    MASS_PER_UNIT_LENGTH = 32
    MEDIUM_LENGTH = 33
    PERCENTAGE = 34
    PRICE = 35
    POWER = 36
    POWER_PER_SMALL_AREA = 37
    PRESSURE_VISCOSITY_COEFFICIENT = 38
    SHORT_LENGTH = 40
    SMALL_ANGLE = 41
    SPECIFIC_HEAT = 42
    STIFFNESS_PER_UNIT_FACE_WIDTH = 43
    STRESS = 44
    TEMPERATURE = 45
    TEMPERATURE_DIFFERENCE = 46
    TEMPERATURE_PER_UNIT_TIME = 47
    THERMAL_CONSTANT = 48
    THERMAL_CONTACT_COEFFICIENT = 49
    THERMAL_EXPANSION_COEFFICIENT = 50
    TORQUE = 51
    TORQUE_CONVERTER_K = 52
    TIME = 53
    TIME_SHORT = 54
    TIME_VERY_SHORT = 55
    UNMEASURABLE = 56
    UNMEASURABLE_INT = 57
    UNMEASURABLE_STRING = 58
    VERY_SHORT_LENGTH = 59
    VELOCITY = 60
    VISCOSITY = 61
    VOLUME = 62
    DAMAGE_RATE = 63
    SAFETY_FACTOR = 64
    VERY_SMALL_ANGLE = 65
    VELOCITY_SMALL = 66
    LINEAR_DAMPING = 67
    LINEAR_ANGULAR_DAMPING = 68
    ANGULAR_JERK = 69
    JERK = 70
    INVERSE_SHORT_LENGTH = 71
    LINEAR_FLEXIBILITY = 72
    THERMO_ELASTIC_FACTOR = 73
    LENGTH_4D = 74
    PRESSURE_VELOCITY_PRODUCT = 75
    QUADRATIC_ANGULAR_DAMPING = 76
    QUADRATIC_DRAG = 77
    MASS_PER_UNIT_TIME = 78
    TORQUE_CONVERTER_INVERSE_K = 79
    INDEX = 80
    HEAT_TRANSFER = 81
    RESCALED_MEASUREMENT = 82
    LENGTH_PER_UNIT_TEMPERATURE = 83
    ANGLE_PER_UNIT_TEMPERATURE = 84
    FORCE_PER_UNIT_TEMPERATURE = 85
    TORQUE_PER_UNIT_TEMPERATURE = 86
    VERY_SHORT_LENGTH_PER_SHORT_LENGTH = 87
    YANK = 88
    ROTATUM = 89
    ANGULAR_COMPLIANCE = 90
    PRESSURE = 91
    FORCE_PER_UNIT_PRESSURE = 92
    MOMENT_PER_UNIT_PRESSURE = 93
    SPECIFIC_ACOUSTIC_IMPEDANCE = 94
    POWER_SMALL = 95
    POWER_SMALL_PER_UNIT_TIME = 97
    ENERGY_SMALL = 98
    HEAT_TRANSFER_FOR_PLASTIC = 99
    HEAT_TRANSFER_RESISTANCE = 100
    WEAR_COEFFICIENT = 101
    INERTIA_PER_UNIT_LENGTH = 102
    INVERSE_SHORT_TIME = 103
    VOLTAGE = 104
    DECIBEL = 105
    DAMAGE = 106
    POWER_SMALL_PER_UNIT_AREA = 107
    PRESSURE_PER_UNIT_TIME = 108
    POWER_SMALL_PER_UNIT_AREA_PER_UNIT_TIME = 109
    POWER_PER_UNIT_TIME = 110


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MeasurementType.__setattr__ = __enum_setattr
MeasurementType.__delattr__ = __enum_delattr


def convert_measurement_to_str(measurement: MeasurementType) -> str:
    words = measurement.name.split('_')
    camel_case = map(lambda x: x.capitalize(), words)
    return ''.join(camel_case)
