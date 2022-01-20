"""Types of the objects contained in the OSEF stream."""
import uuid
from collections import namedtuple

import numpy as np

import osef._unpackers as _unpackers
import osef._packers as _packers
from osef.constants import OsefTypes

LeafInfo = namedtuple("Leaf", "unpack_function pack_function")
InternalNodeInfo = namedtuple("InternalNode", "type")
TypeInfo = namedtuple("Type", "name node_info")


outsight_types = {
    OsefTypes.AUGMENTED_CLOUD.value: TypeInfo(
        "augmented_cloud", InternalNodeInfo(dict)
    ),
    OsefTypes.NUMBER_POINTS.value: TypeInfo(
        "number_of_points",
        LeafInfo(
            _unpackers._get_value_unpacker("<L"), _packers._get_value_packer("<L")
        ),
    ),
    OsefTypes.SPHERICAL_COORD_3F.value: TypeInfo(
        "spherical_coordinates",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("azimuth", np.float32),
                            ("elevation", np.float32),
                            ("distance", np.float32),
                        ]
                    ),
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.REFLECTIVITIES.value: TypeInfo(
        "reflectivities",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.uint8)), _packers._array_packer
        ),
    ),
    OsefTypes.BACKGROUND_FLAG.value: TypeInfo(
        "background_flags",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(bool)), _packers._array_packer
        ),
    ),
    OsefTypes.CARTESIAN_COORD_3F.value: TypeInfo(
        "cartesian_coordinates",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    ([("x", np.float32), ("y", np.float32), ("z", np.float32)]),
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.BGR_COLOR.value: TypeInfo(
        "bgr_colors", LeafInfo(_unpackers._bytes_unpacker, _packers._bytes_packer)
    ),
    OsefTypes.OBJECT_DETECTION_FRAME.value: TypeInfo(
        "object_detection_frame", InternalNodeInfo(dict)
    ),
    OsefTypes.IMAGE_DIM.value: TypeInfo(
        "image_dimension",
        LeafInfo(
            _unpackers._get_dict_unpacker("<LL", ["image_width", "image_height"]),
            _packers._get_dict_packer("<LL", ["image_width", "image_height"]),
        ),
    ),
    OsefTypes.NUMBER_OBJECT.value: TypeInfo(
        "number_of_objects",
        LeafInfo(
            _unpackers._get_value_unpacker("<L"), _packers._get_value_packer("<L")
        ),
    ),
    OsefTypes.CLOUD_FRAME.value: TypeInfo("cloud_frame", InternalNodeInfo(dict)),
    OsefTypes.TIMESTAMP_MICROSECOND.value: TypeInfo(
        "timestamp_microsecond",
        LeafInfo(_unpackers._parse_timestamp, _packers._timestamp_packer),
    ),
    OsefTypes.AZIMUTHS_COL.value: TypeInfo(
        "azimuths_column",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.float32)), _packers._array_packer
        ),
    ),
    OsefTypes.NUMBER_OF_LAYERS.value: TypeInfo(
        "number_of_layers",
        LeafInfo(
            _unpackers._get_value_unpacker("<L"), _packers._get_value_packer("<L")
        ),
    ),
    OsefTypes.CLOUD_PROCESSING.value: TypeInfo(
        "cloud_processing",
        LeafInfo(
            _unpackers._processing_bitfield_unpacker,
            _packers._processing_bitfield_packer,
        ),
    ),
    OsefTypes.RANGE_AZIMUTH.value: TypeInfo(
        "range_azimuth",
        LeafInfo(
            _unpackers._get_dict_unpacker(
                "<ff", ["azimuth_begin_deg", "azimuth_end_deg"]
            ),
            _packers._get_dict_packer("<ff", ["azimuth_begin_deg", "azimuth_end_deg"]),
        ),
    ),
    OsefTypes.BBOX_ARRAY.value: TypeInfo(
        "bounding_boxes_array",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("x_min", np.float32),
                            ("y_min", np.float32),
                            ("x_max", np.float32),
                            ("y_max", np.float32),
                        ]
                    ),
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.CLASS_ID_ARRAY.value: TypeInfo(
        "class_id_array",
        LeafInfo(_unpackers._class_array_unpacker, _packers._class_array_packer),
    ),
    OsefTypes.CONFIDENCE_ARRAY.value: TypeInfo(
        "confidence_array",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.float32)), _packers._array_packer
        ),
    ),
    OsefTypes.TIMESTAMP_DATA.value: TypeInfo(
        "timestamped_data", InternalNodeInfo(dict)
    ),
    OsefTypes.PERCEPT.value: TypeInfo(
        "percept",
        LeafInfo(_unpackers._percept_class_unpacker, _packers._percept_class_packer),
    ),
    OsefTypes.CLUSTER.value: TypeInfo(
        "cluster",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.uint16)), _packers._array_packer
        ),
    ),
    OsefTypes.BGR_IMAGE.value: TypeInfo("bgr_image_frame", InternalNodeInfo(dict)),
    OsefTypes.POSE.value: TypeInfo(
        "pose", LeafInfo(_unpackers._pose_unpacker, _packers._pose_packer)
    ),
    OsefTypes.SCAN_FRAME.value: TypeInfo("scan_frame", InternalNodeInfo(dict)),
    OsefTypes.TRACKED_OBJECT.value: TypeInfo("tracked_objects", InternalNodeInfo(dict)),
    OsefTypes.BOUNDING_BOX_SIZE.value: TypeInfo(
        "bbox_sizes",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("bbox_x", np.float32),
                            ("bbox_y", np.float32),
                            ("bbox_z", np.float32),
                        ]
                    ),
                ),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.SPEED_VECTOR.value: TypeInfo(
        "speed_vectors",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    ([("Vx", np.float32), ("Vy", np.float32), ("Vz", np.float32)]),
                ),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.POSE_ARRAY.value: TypeInfo(
        "pose_array",
        LeafInfo(_unpackers._pose_array_unpacker, _packers._pose_array_packer),
    ),
    OsefTypes.OBJECT_ID.value: TypeInfo(
        "object_id",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.ulonglong)),
            _packers._array_packer,
        ),
    ),
    OsefTypes.CARTESIAN_COORD_4F.value: TypeInfo(
        "cartesian_coordinates_4f",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("x", np.float32),
                            ("y", np.float32),
                            ("z", np.float32),
                            ("__todrop", np.float32),
                        ]
                    ),
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    # __todrop are unused columns that are here to
    # have 4 floats in the TLV which is more cpu efficient.
    OsefTypes.SPHERICAL_COORD_4F.value: TypeInfo(
        "spherical_coordinates_4f",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("azimuth", np.float32),
                            ("elevation", np.float32),
                            ("distance", np.float32),
                            ("__todrop", np.float32),
                        ]
                    ),
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.ZONES.value: TypeInfo("zones_def", InternalNodeInfo(list)),
    OsefTypes.ZONE.value: TypeInfo("zone", InternalNodeInfo(dict)),
    OsefTypes.ZONE_VERTICE.value: TypeInfo(
        "zone_vertices",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(([("x", np.float32), ("y", np.float32)])),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.ZONE_NAME.value: TypeInfo(
        "zone_name",
        LeafInfo(_unpackers._get_string_unpacker(), _packers._get_string_packer()),
    ),
    OsefTypes.ZONE_UUID.value: TypeInfo(
        "zone_uuid", LeafInfo(lambda v: uuid.UUID(bytes=v), lambda v: v.bytes)
    ),
    OsefTypes.ZONE_BINDINGS.value: TypeInfo(
        "zones_objects_binding",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    ([("object_id", np.uint64), ("zone_idx", np.uint32)]),
                ),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.OBJECT_PROPERTIES.value: TypeInfo(
        "object_properties",
        LeafInfo(
            _unpackers._object_properties_unpacker, _packers._object_properties_packer
        ),
    ),
    OsefTypes.IMU_PACKET.value: TypeInfo(
        "imu_packet", LeafInfo(_unpackers._imu_unpacker, _packers._imu_packer)
    ),
    OsefTypes.VELODYNE_TIMESTAMP.value: TypeInfo(
        "timestamp_lidar_velodyne",
        LeafInfo(
            _unpackers._get_dict_unpacker("<LL", ["unix_s", "remaining_us"]),
            _packers._get_dict_packer("<LL", ["unix_s", "remaining_us"]),
        ),
    ),
    OsefTypes.POSE_RELATIVE.value: TypeInfo(
        "pose_relative", LeafInfo(_unpackers._pose_unpacker, _packers._pose_packer)
    ),
    OsefTypes.GRAVITY.value: TypeInfo(
        "gravity",
        LeafInfo(
            _unpackers._get_dict_unpacker("<fff", ["x", "y", "z"]),
            _packers._get_dict_packer("<fff", ["x", "y", "z"]),
        ),
    ),
    OsefTypes.EGO_MOTION.value: TypeInfo("ego_motion", InternalNodeInfo(dict)),
    OsefTypes.PREDICTED_POSITION.value: TypeInfo(
        "predicted_position",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    ([("x", np.float32), ("y", np.float32), ("z", np.float32)]),
                ),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.GEOGRAPHIC_POSE.value: TypeInfo(
        "geographic_pose",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    (
                        [
                            ("lat", np.float32),
                            ("long", np.float32),
                            ("heading", np.float32),
                        ]
                    )
                )
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.OBJECT_ID_32_BITS.value: TypeInfo(
        "object_id_32_bits",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.uint32)), _packers._array_packer
        ),
    ),
    OsefTypes.ZONE_BINDINGS_32_BITS.value: TypeInfo(
        "zones_objects_binding_32_bits",
        LeafInfo(
            _unpackers._get_structured_array_unpacker(
                np.dtype(
                    ([("object_id", np.uint32), ("zone_idx", np.uint32)]),
                ),
            ),
            _packers._structured_array_packer,
        ),
    ),
    OsefTypes.BACKGROUND_BITS.value: TypeInfo(
        "background_bits",
        LeafInfo(_unpackers._bool_bitfield_unpacker, _packers._bool_bitfield_packer),
    ),
    OsefTypes.GROUND_PLANE_BITS.value: TypeInfo(
        "ground_plane_bits",
        LeafInfo(_unpackers._bool_bitfield_unpacker, _packers._bool_bitfield_packer),
    ),
    OsefTypes.AZIMUTHS.value: TypeInfo(
        "azimuths",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.float32)), _packers._array_packer
        ),
    ),
    OsefTypes.ELEVATIONS.value: TypeInfo(
        "elevations",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.float32)), _packers._array_packer
        ),
    ),
    OsefTypes.DISTANCES.value: TypeInfo(
        "distances",
        LeafInfo(
            _unpackers._get_array_unpacker(np.dtype(np.float32)), _packers._array_packer
        ),
    ),
    OsefTypes.LIDAR_MODEL.value: TypeInfo(
        "lidar_model",
        LeafInfo(_unpackers._lidar_model_unpacker, _packers._lidar_model_packer),
    ),
    OsefTypes.SLAM_POSE_ARRAY.value: TypeInfo(
        "slam_pose_array",
        LeafInfo(_unpackers._pose_array_unpacker, _packers._pose_array_packer),
    ),
    OsefTypes.ZONE_VERTICAL_LIMITS.value: TypeInfo(
        "zone_vertical_limits",
        LeafInfo(
            _unpackers._get_array_unpacker(
                np.dtype(np.float32),
            ),
            _packers._array_packer,
        ),
    ),
}


def get_type_info_by_id(type_code):
    """Get TypeInfo for a given type code.

    :param type_code: Int value in OsefTypes
    :return:
    """
    if type_code in outsight_types:
        return outsight_types[type_code]

    return TypeInfo(f"Unknown type ({type_code})", LeafInfo(None, None))


def get_type_info_by_key(type_name: str) -> TypeInfo:
    """Get TypeInfo for a given key/name.

    :param type_name: Int value in OsefTypes
    :return:
    """
    for value in outsight_types.values():
        if value.name == type_name:
            return value
    return TypeInfo(f"Unknown type ({type_name})", LeafInfo(None, None))


def get_type_by_key(type_name: str) -> OsefTypes:
    """Get type index for a given key/name.

    :param type_name: Int value in OsefTypes
    :return:
    """
    for key, value in outsight_types.items():
        if value.name == type_name:
            return OsefTypes(key)
    raise ValueError(f"No type found for type_name={type_name}")
