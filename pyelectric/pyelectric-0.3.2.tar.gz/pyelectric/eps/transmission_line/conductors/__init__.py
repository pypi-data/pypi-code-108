from typing import Any, Dict

from .conductors import conductors_dict


def get_by_name(conductor_name: str) -> Dict[str, Any]:
    return conductors_dict[conductor_name]


def get_radius_by_name(conductor_name: str) -> float:
    return get_by_name(conductor_name)['radius']


def get_gmr_by_name(conductor_name: str) -> float:
    return get_by_name(conductor_name)['gmr']
