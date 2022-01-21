'''_1952.py

DesignEntityId
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DESIGN_ENTITY_ID = python_net_import('SMT.MastaAPI.SystemModel', 'DesignEntityId')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignEntityId',)


class DesignEntityId(Enum):
    '''DesignEntityId

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DESIGN_ENTITY_ID

    __hash__ = None

    ASSEMBLY = 0
    ROLLING_BEARING = 1
    JOURNAL_BEARING = 2
    BEARING = 3
    SHAFT = 4
    PLANET_SHAFT = 5
    CYLINDRICAL_GEAR = 6
    CYLINDRICAL_RING_GEAR = 7
    CYLINDRICAL_SUN_GEAR = 8
    CYLINDRICAL_PLANET_GEAR = 9
    CYLINDRICAL_GEAR_PAIR = 10
    CYLINDRICAL_GEAR_SET = 11
    FE_MESH = 12
    FE_NODE = 13
    CYLINDRICAL_PLANETARY_GEAR_SET = 14
    STRAIGHT_BEVEL_DIFFERENTIAL_GEAR_SET = 15
    SPIRAL_BEVEL_DIFFERENTIAL_GEAR_SET = 16
    ZEROL_BEVEL_DIFFERENTIAL_GEAR_SET = 17
    DATUM = 18
    SPLINE = 19
    CYLINDRICAL_PLANET_CARRIER = 20
    BEVEL_DIFFERENTIAL_PLANET_CARRIER = 21
    SHAFTHUB_CONNECTION = 22
    EXTERNAL_3D_CAD_MODEL = 23
    EXTERNAL_2D_CAD_MODEL = 24
    FE_PART = 25
    DISABLED_FE_PART = 26
    CONICAL_GEAR_SET = 27
    CONICAL_GEAR = 28
    MEASUREMENT_POINT = 29
    WORM_GEAR = 30
    WORM_WHEEL = 31
    WORM_GEAR_SET = 32
    SPIRAL_BEVEL_GEAR = 33
    SPIRAL_BEVEL_GEAR_SET = 34
    STRAIGHT_BEVEL_GEAR = 35
    STRAIGHT_BEVEL_GEAR_SET = 36
    HYPOID_GEAR = 37
    HYPOID_GEAR_SET = 38
    KLINGELNBERG_CYCLOPALLOID_SPIRAL_BEVEL_GEAR = 39
    KLINGELNBERG_CYCLOPALLOID_SPIRAL_BEVEL_GEAR_SET = 40
    KLINGELNBERG_CYCLOPALLOID_HYPOID_GEAR = 41
    KLINGELNBERG_CYCLOPALLOID_HYPOID_GEAR_SET = 42
    ZEROL_GEAR = 43
    ZEROL_GEAR_SET = 44
    POWER_LOAD = 45
    POINT_LOAD = 46
    SPRING_DAMPER = 47
    OIL_SEAL = 48
    MASS_DISC = 49
    BOLT = 50
    BOLTED_JOINT = 51
    ROLLING_RING = 52
    UNBALANCED_MASS = 53
    FLEXIBLE_PIN_ASSEMBLY = 54
    FLEXIBLE_PIN = 55
    BELT_DRIVE = 56
    PULLEY = 57
    TORQUE_CONVERTER = 58
    CVT = 59
    CONCEPT_COUPLING = 60
    CLUTCH = 61
    CONNECTION = 62
    SYNCHRONISER = 63
    CONCEPT_GEAR = 64
    CONCEPT_GEAR_SET = 65
    CYLINDRICAL_GEAR_CLONE = 66
    CYLINDRICAL_RING_GEAR_CLONE = 67
    SUPERCHARGER_ROTOR = 68
    SUPERCHARGER_ROTOR_SET = 69
    CONICAL_GEAR_CLONE = 70
    FACE_GEAR_PINION = 71
    FACE_GEAR_WHEEL = 72
    FACE_GEAR_SET = 73
    PARTTOPART_SHEAR_COUPLING = 74
    CYCLOIDAL_DISC = 75
    RING_PINS = 76
    CYCLOIDAL_ASSEMBLY = 77


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DesignEntityId.__setattr__ = __enum_setattr
DesignEntityId.__delattr__ = __enum_delattr
