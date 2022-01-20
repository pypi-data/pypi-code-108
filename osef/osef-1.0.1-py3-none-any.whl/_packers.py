"""packing functions for osef types"""
from struct import Struct
from typing import List

import numpy as np

from osef.constants import LidarModel


def _get_value_packer(pack_format: str):
    def _pack_value(value: object) -> bytes:
        return Struct(pack_format).pack(value)

    return _pack_value


def _array_packer(value: np.array) -> bytes:
    return value.tobytes()


def _bytes_packer(value: bytes) -> bytes:
    return value


def _get_dict_packer(pack_format: str, fields_names: List[str]):
    def _pack_dict(value: dict) -> bytes:
        values = [value[k] for k in fields_names]
        array = Struct(pack_format).pack(*values)
        return array

    return _pack_dict


def _structured_array_packer(value: np.ndarray) -> bytes:
    return value.tobytes()


def _class_array_packer(value: np.ndarray) -> bytes:
    if len(value) == 0:
        return np.array([]).tobytes()
    array = value["class_code"].astype(np.int32)
    return array.tobytes()


def _timestamp_packer(value: float) -> bytes:
    seconds = int(value)
    micro_seconds = int((value % 1) * 10 ** 6 + 0.5)
    return Struct("<LL").pack(seconds, micro_seconds)


def _pose_packer(value: dict) -> bytes:
    """Values to parse: tx ty tz Vxx Vyx Vzx Vxy Vyy Vzy Vxz Vyz Vzz

    Where rotation matrices should be at the end:
        | Vxx Vxy Vxz |
    R = | Vyx Vyy Vyz |
        | Vzx Vzy Vzz |
    """
    translation = value["translation"]
    rotation = np.ravel(value["rotation"].transpose())
    t_r = np.hstack((translation, rotation)).astype(np.float32)
    return t_r.tobytes()


def _pose_array_packer(value: List) -> bytes:
    if len(value) == 0:
        return np.array([]).tobytes()
    out = bytes()
    for pose in value:
        out = out + _pose_packer(pose)
    return out


def _processing_bitfield_packer(value: dict) -> bytes:
    return Struct("<Q").pack(value["background_deleted"])


def _bool_bitfield_packer(value: np.ndarray) -> bytes:
    return np.packbits(value, bitorder="little").tobytes()


def _percept_class_packer(value: np.ndarray) -> bytes:
    raise NotImplementedError()


def _get_string_packer():
    def _pack_string(value: str) -> bytes:
        return value.encode("ascii") + b"\x00"

    return _pack_string


def _object_properties_packer(value: np.ndarray) -> bytes:
    if len(value) == 0:
        return bytes()
    props = []
    list_arr = list(value.tolist())
    for prop in list_arr:
        props.append(sum([v * (2 ** i) for i, v in enumerate(prop)]))
    return Struct("<%dB" % len(props)).pack(*props)


def _imu_packer(value: dict) -> bytes:
    return Struct("<LLffffff").pack(
        value["timestamp"]["unix_s"],
        value["timestamp"]["remaining_us"],
        value["acceleration"][0],
        value["acceleration"][1],
        value["acceleration"][2],
        value["angular_velocity"][0],
        value["angular_velocity"][1],
        value["angular_velocity"][2],
    )


def _lidar_model_packer(value: LidarModel):
    if len(value) == 0:
        return bytes()
    return Struct("<B").pack(value.id)
