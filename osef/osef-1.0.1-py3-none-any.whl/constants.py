"""Constants used throughout project and that can be used by user"""
from collections import namedtuple
from enum import Enum, IntEnum


class OsefTypes(IntEnum):
    """Outsight Node and Leaf types."""

    AUGMENTED_CLOUD = 1
    NUMBER_POINTS = 2
    SPHERICAL_COORD_3F = 3
    REFLECTIVITIES = 4
    BACKGROUND_FLAG = 5
    CARTESIAN_COORD_3F = 6
    BGR_COLOR = 7
    OBJECT_DETECTION_FRAME = 8
    IMAGE_DIM = 9
    NUMBER_OBJECT = 10
    CLOUD_FRAME = 11
    TIMESTAMP_MICROSECOND = 12
    AZIMUTHS_COL = 13
    NUMBER_OF_LAYERS = 14
    CLOUD_PROCESSING = 15
    RANGE_AZIMUTH = 16
    BBOX_ARRAY = 17
    CLASS_ID_ARRAY = 18
    CONFIDENCE_ARRAY = 19
    TIMESTAMP_DATA = 20
    PERCEPT = 21
    CLUSTER = 22
    BGR_IMAGE = 23
    POSE = 24
    SCAN_FRAME = 25
    TRACKED_OBJECT = 26
    BOUNDING_BOX_SIZE = 27
    SPEED_VECTOR = 28
    POSE_ARRAY = 29
    OBJECT_ID = 30
    CARTESIAN_COORD_4F = 31
    SPHERICAL_COORD_4F = 32
    ZONES = 33
    ZONE = 34
    ZONE_VERTICE = 35
    ZONE_NAME = 36
    ZONE_UUID = 37
    ZONE_BINDINGS = 38
    OBJECT_PROPERTIES = 39
    IMU_PACKET = 40
    VELODYNE_TIMESTAMP = 41
    POSE_RELATIVE = 42
    GRAVITY = 43
    EGO_MOTION = 44
    PREDICTED_POSITION = 45
    GEOGRAPHIC_POSE = 46
    OBJECT_ID_32_BITS = 47
    ZONE_BINDINGS_32_BITS = 48
    BACKGROUND_BITS = 49
    GROUND_PLANE_BITS = 50
    AZIMUTHS = 51
    ELEVATIONS = 52
    DISTANCES = 53
    LIDAR_MODEL = 54
    SLAM_POSE_ARRAY = 55
    ZONE_VERTICAL_LIMITS = 56


class PerceptIds(Enum):
    """Ids of the elements classified by the percept algorithm"""

    DEFAULT = 0
    ROAD = 1
    VEGETATION = 2
    GROUND = 3
    SIGN = 4
    BUILDING = 5
    FLAT_GND = 6
    UNKNOWN = 7
    MARKING = 8
    OBJECT = 9
    WALL = 10


class TrackedObjectClassIds(Enum):
    """Ids of the objects classified by the tracking algorithm"""

    UNKNOWN = 0
    PERSON = 1
    LUGGAGE = 2
    TROLLEY = 3
    TRUCK = 4
    BUS = 5
    CAR = 6
    VAN = 7
    TWO_WHEELER = 8
    MASK = 9
    NO_MASK = 10
    LANDMARK = 11


class LidarModelIds(Enum):
    """LiDAR models enum"""

    UNKNOWN = 0
    VELODYNE_VLP16 = 1
    VELODYNE_VLP32 = 2
    VELODYNE_VLS128 = 3
    VELODYNE_HDL32 = 4
    ROBOSENSE_BPEARL_V1 = 5
    ROBOSENSE_BPEARL_V2 = 6
    ROBOSENSE_RS32 = 7
    ROBOSENSE_HELIOS = 8
    LIVOX_HORIZON = 9
    LIVOX_AVIA = 10
    LIVOX_MID70 = 11
    OUSTER = 12
    OUTSIGHT_SA01 = 13
    HESAI_PANDAR_XT = 14
    HESAI_PANDAR_QT = 15
    RANDOM = 16


LidarModel = namedtuple("LidarModel", ("id", "name"))


# TLV constant
_Tlv = namedtuple("TLV", "type length value")
_TreeNode = namedtuple("TreeNode", "type children leaf_value")
# Structure Format definition (see https://docs.python.org/3/library/struct.html#format-strings):
# Meant to be used as: _STRUCT_FORMAT % length
_STRUCT_FORMAT = "<"  # little endian
_STRUCT_FORMAT += "L"  # unsigned long        (field 'T' ie. 'Type')
_STRUCT_FORMAT += "L"  # unsigned long        (field 'L' ie. 'Length')
_STRUCT_FORMAT += "%ds"  # buffer of fixed size (field 'V' ie. 'Value')
